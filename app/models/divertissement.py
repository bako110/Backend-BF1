from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class Divertissement(Document):
    title: str = Field(..., description="Titre du divertissement")
    category: str = Field(..., description="Catégorie du divertissement")
    image: Optional[HttpUrl] = Field(None, description="Image du divertissement")
    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    description: str = Field(..., description="Description ou contenu du divertissement")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    duration_minutes: Optional[int] = Field(default=30, description="Durée en minutes")
    views: int = Field(default=0, description="Nombre de vues")
    rating: float = Field(default=0, ge=0, le=5, description="Note du divertissement (0 à 5)")

    published_at: Optional[datetime] = Field(None, description="Date de publication")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "divertissements"
