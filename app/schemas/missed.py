from datetime import datetime
from typing import Any, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

class MissedBase(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    tags: list[str] = []
    is_active: bool = True
    is_premium: bool = False
    required_subscription_category: Optional[str] = None
    allow_comments: bool = True
    aired_at: Optional[datetime] = None

class MissedCreate(MissedBase):
    pass

class MissedUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    required_subscription_category: Optional[str] = None
    allow_comments: Optional[bool] = None
    aired_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class MissedResponse(MissedBase):
    id: str = Field(alias="_id")
    views: int = 0
    likes: int = 0
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        return str(v) if v is not None else v

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "title": "Journal du 20h - Édition Spéciale",
                "description": "Retrouvez le journal que vous avez manqué",
                "thumbnail": "https://example.com/thumbnail.jpg",
                "video_url": "https://example.com/video.mp4",
                "duration": 45,
                "views": 1250,
                "likes": 89,
                "category": "JT & Mag",
                "aired_at": "2024-04-07T20:00:00Z",
                "is_premium": False,
                "created_at": "2024-04-07T21:00:00Z",
                "updated_at": "2024-04-07T21:00:00Z"
            }
        }

class MissedListResponse(BaseModel):
    items: list[MissedResponse]
    total: int
    skip: int
    limit: int
