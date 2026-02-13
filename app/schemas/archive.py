from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, Any
from datetime import datetime


class ArchiveBase(BaseModel):
    title: str
    image: Optional[HttpUrl] = None
    thumbnail: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    description: str
    duration_minutes: int
    is_premium: bool = True
    price: float = 0.0
    category: Optional[str] = None
    tags: list[str] = []
    archived_date: datetime
    original_publish_date: Optional[datetime] = None


class ArchiveCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    price: float = 0.0
    archived_date: datetime
    
    @field_validator('thumbnail', 'video_url', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class ArchiveUpdate(BaseModel):
    title: Optional[str] = None
    image: Optional[HttpUrl] = None
    thumbnail: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_premium: Optional[bool] = None
    price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    archived_date: Optional[datetime] = None
    original_publish_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class ArchiveOut(ArchiveBase):
    id: str
    views: int
    rating: float
    rating_count: int
    purchases_count: int
    popularity_score: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        populate_by_name = True
