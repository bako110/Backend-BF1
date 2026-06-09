from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Like(Document):
    user_id: str = Field(..., description="ID de l'utilisateur")
    content_id: str = Field(..., description="ID du contenu")
    content_type: str = Field(..., description="Type de contenu : 'movie', 'show', 'sport', 'jtandmag', 'divertissement', 'reportage', 'archive', 'tele_realite', 'missed', etc.")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "likes"
        indexes = [
            [("content_id", 1), ("content_type", 1)],
            [("user_id", 1)],
            [("user_id", 1), ("content_id", 1), ("content_type", 1)],
        ]
