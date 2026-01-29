from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Notification(Document):
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur concerné")
    title: str = Field(..., description="Titre de la notification")
    message: str = Field(..., description="Message de la notification")
    category: Optional[str] = Field(None, description="Catégorie de notification")
    is_read: bool = Field(False, description="Statut de lecture")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "is_read",
            "created_at",
            [("user_id", 1), ("is_read", 1), ("created_at", -1)]
        ]
