from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .scanner import router as scanner_router
from .products import router as products_router
from .ebay import router as ebay_router
from .auth import router as auth_router


router = APIRouter()

router.include_router(dashboard_router)
router.include_router(scanner_router)
router.include_router(products_router)
router.include_router(ebay_router)
router.include_router(auth_router)