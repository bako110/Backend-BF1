from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class Reportage(Document):
    title: str = Field(..., description="Titre du reportage")
    category: str = Field(..., description="Catégorie du reportage")

    video_url: Optional[HttpUrl] = Field(None, description="URL de la vidéo")
    thumbnail: Optional[HttpUrl] = Field(None, description="Miniature du reportage")

    description: str = Field(..., description="Description du reportage")
    duration_minutes: int = Field(..., description="Durée en minutes")

    program_title: Optional[str] = Field(None, description="Émission d'origine")
    host: Optional[str] = Field(None, description="Animateur / présentateur")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    views: int = Field(default=0, description="Nombre de vues")
    rating: float = Field(default=0, ge=0, le=5, description="Note du reportage (0 à 5)")

    aired_at: datetime = Field(..., description="Date de diffusion originale")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "reportages"
