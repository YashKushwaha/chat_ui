import sys 

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse, StreamingResponse

from pydantic import BaseModel

from routes.chat import *
from routes.settings import QueryRequest, SettingUpdate

from routes import chat, settings

import shutil
import uvicorn
import os
from pathlib import Path
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_dir = os.path.join(PROJECT_ROOT, 'src')
sys.path.append(src_dir)

from src import get_model_list

from src.config_loader import get_config
from src.embedder import load_text_embedder
from src.vectorstore import load_vector_store
from src.rag_pipeline import generate_answer_with_filtering, generate_answer, simple_llm_call
from src.llms import load_llm, OllamaModel

print(Path(__file__).resolve().parents[1] )
config_file = os.path.join(PROJECT_ROOT , "config", "resources.yaml")
config = get_config(config_file)

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# Include routers
app.include_router(chat.router)
app.include_router(settings.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
print('LLM config -> ', config['llm'])

app.mount("/static", StaticFiles(directory=layout_dir), name="static")
app.mount("/images", StaticFiles(directory=os.path.join(layout_dir, 'images')), name="images")

@app.on_event("startup")
async def startup_event():
    app.state.embedder = load_text_embedder(config['embedding'])
    app.state.vectorstore = load_vector_store(config['vector_store'])
    llm_config = config['llm'][config['llm']['provider']]
    llm_config['model'] = ''.join([i for i in model_list if 'phi' in i])
    #app.state.llm = load_llm(llm_config)
    app.state.llm = OllamaModel(llm_config)
    # Initialize global settings
    app.state.settings = {
        "chat_history": False,
        "feature_x_enabled": True,
        "debug_mode": False,
    }
   
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("base.html", {
        "request": request,
        "chat_endpoint": "/chat"
    })

@app.get("/testing", response_class=HTMLResponse)
async def testing_ui(request: Request):
    return templates.TemplateResponse("base.html", {
        "request": request,
        "chat_endpoint": "/test"
    })


@app.post("/chat")
def ask_rag(request:QueryRequest):
    llm = app.state.llm
    stream = False
    if stream:
        # Get generator
        token_generator = simple_llm_call(
            question=request.message,
            llm=llm,
            stream=True)
        return StreamingResponse(
            (token for token in token_generator),
            media_type="text/plain")
    else:
        response = simple_llm_call(
            question=request.message,
            llm=llm,
            stream=False)
        return JSONResponse(content={"response": response})

@app.post("/rag_chat")
def ask_rag(request:QueryRequest):

    embedder = app.state.embedder
    vectorstore = app.state.vectorstore
    llm = app.state.llm
    user_message = request.message
    

    response = generate_answer(
        question=request.message,
        embedder=embedder,
        vectorstore=vectorstore,
        llm=llm
    )
    print(response)
    #response = user_message

    return {"response": user_message}


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