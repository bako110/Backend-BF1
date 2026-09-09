from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime

ALLOWED_CATEGORIES = {"bug", "idea", "compliment", "other"}
ALLOWED_STATUSES = {"new", "reviewed", "archived"}


class FeedbackCreate(BaseModel):
    message: str = Field(..., min_length=3, max_length=2000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    category: str = Field("other")
    email: Optional[str] = Field(None, max_length=200)
    app_version: Optional[str] = Field(None, max_length=50)
    platform: Optional[str] = Field(None, max_length=20)
    device_info: Optional[str] = Field(None, max_length=200)

    @field_validator("category")
    @classmethod
    def _check_category(cls, v: str) -> str:
        return v if v in ALLOWED_CATEGORIES else "other"


class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    is_read: Optional[bool] = None
    admin_note: Optional[str] = Field(None, max_length=2000)

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v not in ALLOWED_STATUSES:
            raise ValueError(f"status doit être l'un de {sorted(ALLOWED_STATUSES)}")
        return v


class FeedbackOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    message: str
    rating: Optional[int] = None
    category: str
    app_version: Optional[str] = None
    platform: Optional[str] = None
    device_info: Optional[str] = None
    status: str
    is_read: bool
    admin_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("id", "user_id", mode="before")
    @classmethod
    def _oid_to_str(cls, v: Any) -> Any:
        return str(v) if v is not None and not isinstance(v, str) else v

    class Config:
        from_attributes = True
