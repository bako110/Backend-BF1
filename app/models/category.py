from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class Category(Document):
    name: str = Field(..., description="Nom de la catégorie", unique=True)
    description: Optional[str] = Field(None, description="Description de la catégorie")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    class Settings:
        name = "categories"
