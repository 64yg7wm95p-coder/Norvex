from datetime import datetime, timezone

from jose import JWTError, jwt

from .security import SECRET_KEY, TOKEN_EXPIRE_DELTA


ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + TOKEN_EXPIRE_DELTA
    payload.update({"exp": expire})

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        return None