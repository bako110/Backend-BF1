from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class AdminNotification(Document):
    title: str = Field(..., description="Titre de la notification")
    message: str = Field(..., description="Message de la notification")
    category: Optional[str] = Field("admin", description="Categorie de notification")
    recipients: int = Field(0, description="Nombre de destinataires")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "admin_notifications"
        indexes = [
            "created_at",
            "category",
        ]
