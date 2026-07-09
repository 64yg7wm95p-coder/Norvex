import os
import secrets
from datetime import timedelta


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY environment variable is required."
    )

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
)

TOKEN_EXPIRE_DELTA = timedelta(
    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)