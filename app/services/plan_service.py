from ..database import get_db_connection


DEFAULT_LIMITS = {
    "free": 20,
    "starter": 500,
    "pro": 5000,
    "business": 20000
}


def get_user_plan(user_id: int) -> str:
    conn = get_db_connection()

    row = conn.execute(
        "SELECT plan FROM users WHERE id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    if not row:
        return "free"

    return row["plan"] or "free"


def get_plan_limit(user_id: int) -> int:
    plan = get_user_plan(user_id)

    return DEFAULT_LIMITS.get(
        plan.lower(),
        DEFAULT_LIMITS["free"]
    )