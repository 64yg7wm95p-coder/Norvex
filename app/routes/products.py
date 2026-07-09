from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..auth.dependencies import get_current_user_from_cookie
from ..database import get_db_connection

router = APIRouter()


@router.get("/api/v1/products")
def products(
    limit: int = 50,
    current_user=Depends(get_current_user_from_cookie)
):
    user_id = current_user["id"]

    conn = get_db_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM products
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit)
    ).fetchall()

    conn.close()

    return JSONResponse(
        content={
            "user_id": user_id,
            "data": [dict(row) for row in rows]
        }
    )