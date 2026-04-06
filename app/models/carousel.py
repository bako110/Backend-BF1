from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class CarouselItem(Document):
    title: str = Field(..., description="Titre de la slide")
    description: Optional[str] = Field(None, description="Description courte")
    image_url: str = Field(..., description="URL de l'image (Cloudinary)")
    cloudinary_public_id: Optional[str] = Field(None, description="ID public Cloudinary pour suppression")
    order: int = Field(default=0, description="Ordre d'affichage (0 = premier)")
    is_active: bool = Field(True, description="Visible sur le site ?")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        name = "carousel_items"
        indexes = ["order", "is_active", "created_at"]
