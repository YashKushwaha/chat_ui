from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates



from passlib.context import CryptContext

templates = Jinja2Templates(directory="ui/templates")
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simulated user DB
USERS = {
    "testuser": pwd_context.hash("testpass")
}

def get_current_user(request: Request):
    return request.session.get("user")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    hashed = USERS.get(username)
    if hashed and pwd_context.verify(password, hashed):
        request.session["user"] = username
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

"""
@router.get("/", response_class=HTMLResponse)
def home(request: Request, user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})
"""