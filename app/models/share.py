from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class Share(Document):
    user_id: str = Field(..., description="ID de l'utilisateur")
    content_id: str = Field(..., description="ID du contenu")
    content_type: str = Field(..., description="Type de contenu")
    platform: Optional[str] = Field(None, description="Plateforme de partage")
    message: Optional[str] = Field(None, description="Message optionnel")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "shares"
        indexes = [
            "user_id",
            ["content_id", "content_type"],
            [("user_id", 1), ("content_id", 1), ("content_type", 1)]
        ]