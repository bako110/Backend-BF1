

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Favorite(Document):
    user_id: str = Field(..., description="ID de l'utilisateur")
    show_id: Optional[str] = Field(None, description="ID de l'émission favorite")
    movie_id: Optional[str] = Field(None, description="ID du film favori")
    # channel_id: Optional[str] = Field(None, description="ID de la chaîne favorite")
    added_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "favorites"
        indexes = [
            "user_id",
            "show_id",
            "movie_id",
            [("user_id", 1), ("show_id", 1)],
            [("user_id", 1), ("movie_id", 1)]
        ]
