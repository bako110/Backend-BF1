from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, List


class TeleRealite(Document):
    title: str = Field(..., description="Titre de l'émission ou de l'événement")
    category: str = Field(..., description="Catégorie : Télé-réalité, Événement, Concours, etc.")
    sub_type: str = Field(default="tele_realite", description="tele_realite | event")

    video_url: Optional[str] = Field(None, description="URL de la vidéo")
    thumbnail: Optional[str] = Field(None, description="Miniature")
    image: Optional[str] = Field(None, description="Image principale")

    description: Optional[str] = Field(None, description="Description de l'émission ou de l'événement")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Durée en minutes")

    host: Optional[str] = Field(None, description="Animateur / présentateur")
    location: Optional[str] = Field(None, description="Lieu de l'événement (si applicable)")
    participants: List[str] = Field(default_factory=list, description="Participants ou candidats")

    allow_comments: bool = Field(default=True, description="Autoriser les commentaires")
    is_live: bool = Field(default=False, description="Événement en direct")
    is_upcoming: bool = Field(default=False, description="Événement à venir")

    views: int = Field(default=0, description="Nombre de vues")
    likes: int = Field(default=0, description="Nombre de likes")
    rating: float = Field(default=0, ge=0, le=5, description="Note (0 à 5)")

    aired_at: Optional[datetime] = Field(None, description="Date de diffusion")
    event_date: Optional[datetime] = Field(None, description="Date de l'événement (si applicable)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)

    class Settings:
        name = "tele_realite"
        indexes = [
            "category",
            "sub_type",
            "is_live",
            "is_upcoming",
            [("created_at", -1)],
            [("sub_type", 1), ("created_at", -1)],
            [("title", "text"), ("description", "text")],
        ]
