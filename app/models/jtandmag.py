from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class JTandMag(Document):
    title: str = Field(..., description="Titre de l'émission")
    category: str = Field(..., description="Catégorie")
    image: Optional[str] = Field(None, description="Image de l'émission")
    video_url: Optional[str] = Field(None, description="URL de la vidéo (YouTube ou directe)")
    description: Optional[str] = Field(None, description="Description")
    host: Optional[str] = Field(None, description="Animateur / présentateur")
    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")

    views: int = Field(default=0, description="Nombre de vues")
    likes: int = Field(default=0, description="Nombre de likes")
    rating: float = Field(default=0, ge=0, le=5, description="Note (0 à 5)")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "jtandmag"
        indexes = [
            "category",
            [("created_at", -1)],
            [("category", 1), ("created_at", -1)],
            [("views", -1)],
            [("title", "text"), ("description", "text")],
        ]
