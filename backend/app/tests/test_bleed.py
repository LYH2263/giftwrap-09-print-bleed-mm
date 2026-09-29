import pytest
from fastapi import HTTPException

import app.db as db
from app import seed
from app.engines.wrap_math import BLEED_FORMULA, paper_area
from app.repositories import history, settings_repo
from app.services import estimate_service


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "t.db")
    seed.init_db()
    yield


def test_bleed_zero_keeps_original_geometry():
    r = paper_area(0.30, 0.20, 0.15, 1.15, 0)
    assert (r["eff_length"], r["eff_width"], r["eff_height"]) == (0.30, 0.20, 0.15)
    assert r["paper_m2"] == 0.31  # 与无出血基线一致


def test_bleed_expands_geometry_before_overlap():
    r = paper_area(1, 1, 1, 1.5, 50)  # 50mm 出血 → 每边 1.1m
    assert (r["eff_length"], r["eff_width"], r["eff_height"]) == (1.1, 1.1, 1.1)
    assert r["box_surface"] == 7.26          # 先扩边：2*(1.1²*3)
    assert r["paper_m2"] == 10.89            # 再乘折边系数：7.26*1.5
    assert r["formula"] == BLEED_FORMULA


def test_negative_bleed_rejected():
    with pytest.raises(ValueError):
        paper_area(1, 1, 1, 1.15, -0.1)


def test_estimate_negative_bleed_422(tmp_db):
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, "cross", False, "", -5)
    assert ei.value.status_code == 422


def test_saved_run_pinned_after_default_change(tmp_db):
    settings_repo.set_value("bleed_mm", "10")
    res = estimate_service.run_estimate(1, None, "cross", True, "", None)
    rid = res["run_id"]
    assert res["bleed_mm"] == 10.0
    assert rid is not None

    # 写入后改默认出血 —— 不得影响已落库的这一单
    settings_repo.set_value("bleed_mm", "40")

    listed = next(r for r in history.list_runs() if r["id"] == rid)
    detail = history.get_run(rid)
    for r in (listed, detail):  # 列表与详情两路一致，且钉住写入值
        assert r["bleed_mm"] == 10.0
        assert r["paper_m2"] == res["paper_m2"]
        assert (r["eff_length"], r["eff_width"], r["eff_height"]) == (
            res["eff_length"], res["eff_width"], res["eff_height"])
        assert r["result"]["formula"] == BLEED_FORMULA
    assert listed["paper_m2"] == detail["paper_m2"]

    # 互证：算纸台按写入时出血再干算，结果须与回看一致
    dry = estimate_service.run_estimate(1, None, "cross", False, "", 10)
    assert dry["paper_m2"] == detail["paper_m2"]
    assert dry["eff_length"] == detail["eff_length"]

    # 新默认只影响新估算，不回溯已写入的档
    defaulted = estimate_service.run_estimate(1, None, "cross", False, "", None)
    assert defaulted["bleed_mm"] == 40.0
    assert defaulted["paper_m2"] != detail["paper_m2"]
