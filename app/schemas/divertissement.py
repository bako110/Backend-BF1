from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class DivertissementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre du divertissement")
    category: str = Field(..., min_length=1, max_length=80, description="Catégorie")
    image: Optional[HttpUrl] = Field(None, description="Image du divertissement")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    description: str = Field(..., min_length=1, max_length=5000, description="Description ou contenu du divertissement")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    duration_minutes: Optional[int] = Field(default=30, ge=1, le=600, description="Durée en minutes")
    rating: float = Field(default=0, ge=0, le=5, description="Note du divertissement (0 à 5)")

    published_at: Optional[datetime] = Field(None, description="Date de publication")

    @validator("image", "video_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class DivertissementCreate(DivertissementBase):
    pass


class DivertissementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=80)
    image: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    allow_comments: Optional[bool] = None

    duration_minutes: Optional[int] = Field(None, ge=1, le=600)
    rating: Optional[float] = Field(None, ge=0, le=5)

    published_at: Optional[datetime] = None


class DivertissementOut(DivertissementBase):
    id: str
    views: int = Field(0, ge=0, description="Nombre de vues")
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
