from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class LiveHighlight(Document):
    """Mise en avant du LiveScreen mobile — sections 'A ne pas manquer' et 'Moments forts'"""
    section: str = Field(..., description="a_ne_pas_manquer | moments_forts")
    title: str = Field(..., description="Titre de l'émission")
    description: Optional[str] = Field(None, description="Description courte")
    image_url: str = Field(..., description="Affiche")
    video_url: Optional[str] = Field(None, description="Bande-annonce (optionnelle)")
    file_public_id: Optional[str] = Field(None, description="Chemin relatif de l'image pour suppression")
    video_public_id: Optional[str] = Field(None, description="Chemin relatif de la vidéo pour suppression")
    event_date: Optional[datetime] = Field(None, description="Date/heure de l'émission (optionnelle)")
    order: int = Field(default=0, description="Ordre d'affichage (0 = premier)")
    is_active: bool = Field(True, description="Visible sur l'app ?")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "live_highlights"
        indexes = ["section", "order", "is_active", "event_date"]
