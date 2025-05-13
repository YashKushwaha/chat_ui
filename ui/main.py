import os
from pathlib import Path

from src import get_model_list
from src.config_loader import get_config
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import chat, settings, ui, upload, config as config_routes
from config.settings import STATIC_DIR, IMAGES_DIR, PROJECT_ROOT
from events.startup import create_startup_handler


app = FastAPI(
    title="My Cool API",
    description="This API does awesome stuff.",
    version="1.0.0",
    docs_url="/doc",
    redoc_url='/redoc',
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Routers
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(ui.router)
app.include_router(upload.router)
app.include_router(config_routes.router)

# Static
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Event
config_file = os.path.join(PROJECT_ROOT , "config", "resources.yaml")
config = get_config(config_file)
model_list =  get_model_list()
on_startup = create_startup_handler(app, config, model_list)
app.add_event_handler("startup", on_startup)

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="0.0.0.0", port=8000, reload=True)
