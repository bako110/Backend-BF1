from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class SubscriptionPlanBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    duration_months: int = Field(..., ge=1, le=60)
    price_cents: int = Field(..., ge=0)
    currency: str = Field("XOF", min_length=3, max_length=3)
    is_active: bool = True


class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass


class SubscriptionPlanUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_months: Optional[int] = Field(None, ge=1, le=60)
    price_cents: Optional[int] = Field(None, ge=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    is_active: Optional[bool] = None


class SubscriptionPlanOut(SubscriptionPlanBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
