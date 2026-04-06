from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional, List
from bson import ObjectId


class TeleRealiteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre")
    category: str = Field(..., min_length=1, max_length=80, description="Catégorie")
    sub_type: str = Field(default="tele_realite", description="tele_realite | event")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    thumbnail: Optional[HttpUrl] = Field(None, description="Miniature")
    image: Optional[HttpUrl] = Field(None, description="Image principale")
    description: str = Field(..., min_length=1, max_length=5000, description="Description")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Durée en minutes")
    host: Optional[str] = Field(None, min_length=1, max_length=120, description="Animateur")
    location: Optional[str] = Field(None, min_length=1, max_length=200, description="Lieu")
    participants: List[str] = Field(default_factory=list, description="Participants")
    allow_comments: bool = Field(default=True)
    is_live: bool = Field(default=False)
    is_upcoming: bool = Field(default=False)
    aired_at: Optional[datetime] = Field(None, description="Date de diffusion")
    event_date: Optional[datetime] = Field(None, description="Date de l'événement")

    @validator("video_url", "thumbnail", "image", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class TeleRealiteCreate(TeleRealiteBase):
    pass


class TeleRealiteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=80)
    sub_type: Optional[str] = None
    video_url: Optional[HttpUrl] = None
    thumbnail: Optional[HttpUrl] = None
    image: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    host: Optional[str] = Field(None, min_length=1, max_length=120)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    participants: Optional[List[str]] = None
    allow_comments: Optional[bool] = None
    is_live: Optional[bool] = None
    is_upcoming: Optional[bool] = None
    aired_at: Optional[datetime] = None
    event_date: Optional[datetime] = None


class TeleRealiteOut(TeleRealiteBase):
    id: str
    views: int = Field(0, ge=0)
    likes: int = Field(0, ge=0)
    rating: float = Field(0, ge=0, le=5)
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
