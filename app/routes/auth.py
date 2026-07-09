from fastapi import APIRouter, HTTPException, Response, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..auth.user_store import create_user, authenticate_user
from ..auth.jwt_handler import create_access_token

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"error": None}
    )


@router.post("/login")
def login_form(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={"error": "Kullanıcı adı veya şifre hatalı."}
        )

    user_plan = user.get("plan", "free")

    token = create_access_token({
        "sub": str(user["id"]),
        "username": user["username"],
        "plan": user_plan
    })

    redirect = RedirectResponse(
        url="/dashboard",
        status_code=303
    )

    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    return redirect


@router.post("/api/v1/auth/register")
def register(request: RegisterRequest):
    success = create_user(
        request.username,
        request.password
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Bu kullanıcı adı zaten kullanılıyor."
        )

    return {
        "success": True,
        "message": "Kullanıcı oluşturuldu."
    }


@router.post("/api/v1/auth/login")
def login_api(request: LoginRequest, response: Response):
    user = authenticate_user(
        request.username,
        request.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Kullanıcı adı veya şifre hatalı."
        )

    user_plan = user.get("plan", "free")

    token = create_access_token({
        "sub": str(user["id"]),
        "username": user["username"],
        "plan": user_plan
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24
    )

    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "plan": user_plan
        }
    }


@router.post("/api/v1/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token")

    return {
        "success": True,
        "message": "Çıkış yapıldı."
    }