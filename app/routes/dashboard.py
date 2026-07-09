from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..auth.dependencies import get_current_user_from_cookie

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home():
    return RedirectResponse("/dashboard")


@router.get("/dashboard")
def dashboard(
    request: Request,
    current_user=Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={
            "user_id": current_user["id"],
            "username": current_user["username"],
            "plan": current_user["plan"]
        }
    )