from fastapi import FastAPI, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import shutil
import uvicorn
import os

import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

print('PROJECT_ROOT -> ', PROJECT_ROOT)

src_dir = os.path.join(PROJECT_ROOT, 'src')
sys.path.append(src_dir)

from src import get_model_list

from src.config_loader import get_config

#config = get_config('config/index_creation.yaml')

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
layout = 'basic_layout'
UI_BASE = os.path.join(PROJECT_ROOT, 'ui')
layout_dir = os.path.join(UI_BASE, 'static','my_layout')
templates_dir = os.path.join(UI_BASE, 'templates')
templates = Jinja2Templates(directory=templates_dir)

model_list =  get_model_list()
print(model_list)

app.mount("/static", StaticFiles(directory=layout_dir), name="static")
app.mount("/images", StaticFiles(directory=os.path.join(layout_dir, 'images')), name="images")

@app.get("/old", response_class=HTMLResponse)
async def root():
    with open(f"static/{layout}/index.html", "r") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    # Mock response – replace with your LLM/RAG logic
    response_message = f"Echo: {user_message}"
    return {"response": response_message}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File '{file.filename}' uploaded successfully"}

@app.get("/config")
def get_config():
    return {"api_url": "http://127.0.0.1:8000/chat", "api_key": "your-api-key"}


if __name__ == "__main__":
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="0.0.0.0", port=8000, reload=True)