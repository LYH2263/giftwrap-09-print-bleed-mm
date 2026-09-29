import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(box_id, overlap, result, note="", bleed_mm=0.0):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,bleed_mm,result_json,note,created_at) VALUES (?,?,?,?,?,?)",
            (box_id, overlap, float(bleed_mm), json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _row_to_run(row):
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
    return d

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id ORDER BY r.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [_row_to_run(row) for row in rows]
    finally:
        c.close()

def get_run(run_id):
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id WHERE r.id=?""",
            (run_id,),
        ).fetchone()
        return _row_to_run(row) if row else None
    finally:
        c.close()
