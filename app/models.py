from pydantic import BaseModel, Field


class BulkScanRequest(BaseModel):
    user_id: int = 1
    site_url: str
    limit: int = Field(default=4, ge=1, le=250)