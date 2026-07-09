from fastapi import Cookie, HTTPException

from .jwt_handler import decode_access_token


def get_current_user_from_cookie(
    access_token: str | None = Cookie(default=None)
):
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Giriş yapmalısınız."
        )

    payload = decode_access_token(access_token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Geçersiz oturum."
        )

    return {
        "id": int(payload["sub"]),
        "username": payload["username"],
        "plan": payload.get("plan", "free")
    }