from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Comment(Document):
    user_id: str = Field(..., description="ID de l'utilisateur")
    content_id: str = Field(..., description="ID du contenu (movie ou show)")
    content_type: str = Field(..., description="Type de contenu : 'movie' ou 'show'")
    text: str = Field(..., description="Texte du commentaire")
    is_hidden: bool = Field(False, description="Commentaire masqué (modération)")
    hidden_at: Optional[datetime] = Field(None)
    hidden_by: Optional[str] = Field(None, description="ID admin ayant masqué")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)

    class Settings:
        name = "comments"
        indexes = [
            ["content_id", "content_type"],
            ["user_id"]
        ]
