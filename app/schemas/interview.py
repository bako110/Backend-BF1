from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class InterviewBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre de l'interview")
    guest_name: str = Field(..., min_length=1, max_length=120, description="Nom de l'invité")
    guest_role: str = Field(..., min_length=1, max_length=120, description="Rôle ou fonction de l'invité")

    image: Optional[HttpUrl] = Field(None, description="Image de l'interview")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    description: str = Field(..., min_length=1, max_length=5000, description="Description ou contenu de l'interview")

    duration_minutes: int = Field(..., ge=1, le=600, description="Durée en minutes")
    views: int = Field(default=0, ge=0, description="Nombre de vues")
    rating: float = Field(default=0, ge=0, le=5, description="Note de l'interview (0 à 5)")

    published_at: Optional[datetime] = Field(None, description="Date de publication")

    @validator("image", "video_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class InterviewCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre de l'interview")
    guest_name: str = Field(..., min_length=1, max_length=120, description="Nom de l'invité")
    description: str = Field(..., min_length=1, max_length=5000, description="Description ou contenu de l'interview")
    image: Optional[HttpUrl] = Field(None, description="Image de l'interview")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")

    @validator("image", "video_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class InterviewUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    guest_name: Optional[str] = Field(None, min_length=1, max_length=120)
    guest_role: Optional[str] = Field(None, min_length=1, max_length=120)

    image: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)

    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    views: Optional[int] = Field(None, ge=0)
    rating: Optional[float] = Field(None, ge=0, le=5)

    published_at: Optional[datetime] = None


class InterviewOut(InterviewBase):
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
