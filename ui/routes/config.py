from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
def get_config():
    return {"api_url": "http://127.0.0.1:8000/chat", "api_key": "your-api-key"}
