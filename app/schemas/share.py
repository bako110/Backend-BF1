from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

ContentType = Literal[
    "movie",
    "show",
    "breaking_news",
    "interview",
    "reel",
    "replay",
    "trending_show",
    "popular_program"
]


class ShareBase(BaseModel):
    content_id: str = Field(..., description="ID du contenu")
    content_type: ContentType = Field(..., description="Type de contenu")
    platform: Optional[str] = Field(None, max_length=50, description="Plateforme de partage")
    message: Optional[str] = Field(None, max_length=500, description="Message optionnel")


class ShareCreate(ShareBase):
    pass


class ShareOut(ShareBase):
    id: str
    user_id: str
    created_at: datetime

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True