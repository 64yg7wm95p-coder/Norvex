from pydantic import BaseModel
from typing import Optional

# 1. Tarama isteği modeli
class BulkScanRequest(BaseModel):
    shopify_url: str
    limit: int

# 2. Ürün verisi modeli (Frontend'in beklediği format)
class ProductSchema(BaseModel):
    id: int
    original_name: str
    ai_title: str
    original_price: float
    ebay_price: float
    image_url: str
    description: Optional[str] = None

    class Config:
        from_attributes = True # Pydantic v2 için 'orm_mode' yerine kullanılır