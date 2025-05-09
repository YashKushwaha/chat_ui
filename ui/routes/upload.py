import shutil
from fastapi import File, UploadFile

from fastapi import APIRouter
from config.settings import UPLOAD_DIR

router = APIRouter()


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File '{file.filename}' uploaded successfully"}