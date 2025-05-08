from pydantic import BaseModel
from fastapi import APIRouter
from .settings import QueryRequest
router = APIRouter()

@router.post("/test")
async def chat(request: QueryRequest):
    print('User input received -> ', request.message)
    return {"response": request.message}


@router.post("/echo")
async def chat(request: QueryRequest):
    data = await request.json()
    user_message = data.get("message", "")
    response_message = f"Echo: {user_message}"
    return {"response": response_message}
