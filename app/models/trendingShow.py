from beanie import Document
from pydantic import HttpUrl, Field
from datetime import datetime
from typing import Optional


class TrendingShow(Document):
    title: str = Field(..., description="Titre de l'émission")
    category: str = Field(..., description="Catégorie")
    image: Optional[HttpUrl] = Field(None, description="Image de l'émission")
    video_url: Optional[str] = Field(None, description="URL de la vidéo (YouTube ou directe)")
    description: str = Field(..., description="Description")
    host: str = Field(..., description="Animateur / présentateur")

    episodes: int = Field(..., description="Nombre d'épisodes")
    views: int = Field(default=0, description="Nombre de vues")
    rating: float = Field(default=0, ge=0, le=5, description="Note (0 à 5)")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "trendingShows"
