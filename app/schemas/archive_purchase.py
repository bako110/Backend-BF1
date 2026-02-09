from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime


class ArchivePurchaseCreate(BaseModel):
    archive_id: str
    payment_method: str
    transaction_id: Optional[str] = None


class ArchivePurchaseOut(BaseModel):
    id: str
    user_id: str
    archive_id: str
    amount_paid: float
    currency: str
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    purchased_at: datetime
    expires_at: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        populate_by_name = True
