from ..database import get_db_connection
from .password import hash_password, verify_password


def create_user(username: str, password: str) -> bool:
    conn = get_db_connection()

    try:
        conn.execute(
            """
            INSERT INTO users (
                username,
                password_hash
            )
            VALUES (?, ?)
            """,
            (
                username,
                hash_password(password)
            )
        )

        conn.commit()
        return True

    except Exception:
        return False

    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    if not user:
        return None

    user_dict = dict(user)

    if not verify_password(
        password,
        user_dict["password_hash"]
    ):
        return None

    return user_dict