from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class News(Document):
    title: str = Field(..., description="Titre de l'actualité")
    content: str = Field(..., description="Contenu complet de l'actualité")
    image_url: Optional[str] = Field(None, description="Image associée à l'actualité")
    published_at: datetime = Field(default_factory=datetime.utcnow, description="Date de publication")
    author: Optional[str] = Field(None, description="Auteur de l'article")
    edition: Optional[str] = Field(None, description="Édition du journal (13H30, 19H30, etc.)")
    is_live: bool = Field(False, description="Journal en direct ?")
    live_url: Optional[str] = Field(None, description="URL du flux vidéo en direct")

    class Settings:
        name = "news"
        indexes = [
            "edition",
            "is_live",
            "published_at",
            [("edition", 1), ("published_at", -1)]
        ]
