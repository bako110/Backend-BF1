from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class ViewLog(Document):
    """Log de vues pour l'anti-doublon 24h (tous types de contenus)"""
    content_id: str = Field(..., description="ID du contenu")
    content_type: str = Field(..., description="Type : reel, breaking_news, etc.")
    identifier: str = Field(..., description="user_id ou IP")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "view_logs"
        indexes = [
            [("content_id", 1), ("content_type", 1), ("identifier", 1), ("created_at", -1)],
        ]
