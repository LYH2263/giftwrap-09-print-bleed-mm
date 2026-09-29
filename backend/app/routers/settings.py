from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()

class SettingUpdate(BaseModel):
    key: str
    value: float

@router.get("/settings")
def settings(): return settings_repo.get_all()

@router.put("/settings")
def update_setting(body: SettingUpdate):
    if body.key == "bleed_mm":
        if body.value < 0:
            raise HTTPException(422, "bleed_mm must be >= 0")
    elif body.key == "overlap":
        if body.value <= 0:
            raise HTTPException(422, "overlap must be > 0")
    else:
        raise HTTPException(400, "unknown setting key")
    settings_repo.set_value(body.key, body.value)
    return settings_repo.get_all()
