from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..auth.dependencies import get_current_user_from_cookie
from ..models import BulkScanRequest
from ..services import SCAN_STATUS, run_shopify_scan
from ..services.plan_service import get_plan_limit

router = APIRouter()


@router.post("/api/v1/scan/bulk")
def trigger_scan(
    request: BulkScanRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user_from_cookie)
):
    user_id = current_user["id"]
    plan_limit = get_plan_limit(user_id)

    if not request.site_url.startswith("http"):
        raise HTTPException(
            status_code=400,
            detail="Geçersiz URL"
        )

    if request.limit > plan_limit:
        raise HTTPException(
            status_code=403,
            detail=f"{current_user['plan'].upper()} plan en fazla {plan_limit} ürün tarayabilir."
        )

    background_tasks.add_task(
        run_shopify_scan,
        request.site_url,
        request.limit,
        user_id
    )

    return {
        "success": True,
        "message": "Tarama başlatıldı.",
        "plan": current_user["plan"],
        "limit": request.limit,
        "max_limit": plan_limit
    }


@router.get("/api/v1/scan/progress")
def scan_progress(
    current_user=Depends(get_current_user_from_cookie)
):
    return SCAN_STATUS