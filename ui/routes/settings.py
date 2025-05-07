from pydantic import BaseModel
from fastapi import APIRouter
# Input schema
class QueryRequest(BaseModel):
    message: str

class SettingUpdate(BaseModel):
    key: str
    value: bool

router = APIRouter()

@router.get("/settings")
def get_settings():
    return router.state.settings

@router.post("/settings")
def update_setting(update: SettingUpdate):
    if update.key not in router.state.settings:
        return {"error": "Invalid setting key"}
    router.state.settings[update.key] = update.value
    return {"message": f"{update.key} updated", "settings": router.state.settings}
