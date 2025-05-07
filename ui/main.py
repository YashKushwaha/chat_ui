from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import shutil
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#layout = 'basic_layout'
layout = 'my_layout'


app.mount("/static", StaticFiles(directory=f"static/{layout}"), name="static")
app.mount("/images", StaticFiles(directory=f"static/{layout}/images"), name="images")

@app.get("/", response_class=HTMLResponse)
async def root():
    with open(f"static/{layout}/index.html", "r") as f:
        return f.read()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    # Mock response – replace with your LLM/RAG logic
    response_message = f"Echo: {user_message}"
    return {"response": response_message}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File '{file.filename}' uploaded successfully"}

@app.get("/config")
def get_config():
    return {"api_url": "http://127.0.0.1:8000/chat", "api_key": "your-api-key"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",              # import path to your FastAPI app
        reload=True,            # enables auto-reload on code changes
        timeout_keep_alive=1,   # short timeout for idle connections
        host="127.0.0.1",       # optional: specify host
        port=8000               # optional: specify port
    )