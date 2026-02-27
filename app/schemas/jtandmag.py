from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class JTandMagBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre de l'émission")
    category: str = Field(..., min_length=1, max_length=80, description="Catégorie")
    image: Optional[HttpUrl] = Field(None, description="Image de l'émission")
    video_url: Optional[str] = Field(None, description="URL de la vidéo (YouTube ou directe)")
    description: str = Field(..., min_length=1, max_length=5000, description="Description")
    host: Optional[str] = Field(None, min_length=1, max_length=120, description="Animateur / présentateur")
    edition: Optional[str] = Field(None, min_length=1, max_length=50, description="Édition ou saison")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    rating: float = Field(default=0, ge=0, le=5, description="Note (0 à 5)")

    @validator("image", "video_url", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class JTandMagCreate(JTandMagBase):
    pass


class JTandMagUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=80)
    image: Optional[HttpUrl] = None
    video_url: Optional[str] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    host: Optional[str] = Field(None, min_length=1, max_length=120)
    edition: Optional[str] = Field(None, min_length=1, max_length=50)
    allow_comments: Optional[bool] = None

    rating: Optional[float] = Field(None, ge=0, le=5)


class JTandMagOut(JTandMagBase):
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
