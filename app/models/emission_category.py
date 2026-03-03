from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class EmissionCategory(Document):
    name: str = Field(..., description="Nom de la catégorie d'émission")
    image_main: Optional[str] = Field(None, description="URL de l'image principale")
    image_background: Optional[str] = Field(None, description="URL de l'image de fond")
    image_icon: Optional[str] = Field(None, description="URL de l'icône")
    order: int = Field(default=0, description="Ordre d'affichage")
    is_active: bool = Field(default=True, description="Catégorie active ou non")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "emission_categories"
