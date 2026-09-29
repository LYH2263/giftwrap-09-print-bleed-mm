# 口径 bleed_then_overlap:v1 —— 出血扩边先作用于盒体几何（每边外扩 bleed_mm），
# 折边系数后作用于扩边后的表面积。该口径随单固化（写入 result.formula），不得静默更改。
BLEED_FORMULA = "bleed_then_overlap:v1"


def paper_area(length: float, width: float, height: float, overlap: float = 1.15, bleed_mm: float = 0.0) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    bleed_mm = float(bleed_mm)
    if bleed_mm < 0:
        raise ValueError("bleed_mm must be >= 0")
    b = bleed_mm / 1000.0
    el, ew, eh = L + 2 * b, W + 2 * b, H + 2 * b
    base = 2 * (el * ew + el * eh + ew * eh)
    need = base * float(overlap)
    return {
        "box_surface": round(base, 3),
        "overlap": float(overlap),
        "bleed_mm": bleed_mm,
        "eff_length": round(el, 4),
        "eff_width": round(ew, 4),
        "eff_height": round(eh, 4),
        "paper_m2": round(need, 3),
        "formula": BLEED_FORMULA,
    }


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
