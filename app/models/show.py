from beanie import Document
from pydantic import Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class Show(Document):
    title: str = Field(..., description="Titre de l'émission")
    description: Optional[str] = Field(None, description="Description")
    host: Optional[str] = Field(None, description="Animateur / présentateur")
    category: Optional[str] = Field(None, description="Catégorie")

    image_url: Optional[HttpUrl] = Field(None, description="Image de l'émission")

    # Flux unique
    is_live: bool = Field(False, description="En direct ?")
    stream_url: Optional[HttpUrl] = Field(None, description="URL du flux unique (live ou replay)")

    # Replay
    is_replay: bool = Field(False, description="Disponible en replay ?")
    replay_at: Optional[datetime] = Field(None, description="Date de diffusion")

    # Engagement
    views: int = Field(0, description="Nombre de vues")
    is_featured: bool = Field(False, description="Mis en avant")
    tags: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "shows"
        indexes = [
            "category",
            "is_live",
            "is_featured",
            "replay_at"
        ]
