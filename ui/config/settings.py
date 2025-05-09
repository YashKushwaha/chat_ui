import os
from fastapi.templating import Jinja2Templates

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
UI_BASE = os.path.join(PROJECT_ROOT, "ui")
STATIC_DIR = os.path.join(UI_BASE, "static", "my_layout")
IMAGES_DIR = os.path.join(STATIC_DIR, "images")
TEMPLATES_DIR = os.path.join(UI_BASE, "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)