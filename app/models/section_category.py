from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


# Valeurs fixes des grandes sections — à utiliser comme clé `section`
SECTIONS = {
    "flash_infos": "Flash Infos",
    "jtandmag": "JT et Mag",
    "reportage": "Reportages",
    "divertissement": "Divertissement et Mag",
    "sport": "Sport",
    "tele_realite": "Télé Réalité et Événements",
}


class SectionCategory(Document):
    """Sous-catégorie rattachée à une grande section de BF1."""

    section: str = Field(
        ...,
        description=(
            "Grande section parente. Valeurs : "
            "flash_infos | jtandmag | reportage | divertissement | sport | tele_realite"
        ),
    )
    name: str = Field(..., description="Nom de la sous-catégorie (ex: 13h, LTS, Marathon)")
    slug: Optional[str] = Field(None, description="Slug URL-friendly généré automatiquement")
    description: Optional[str] = Field(None, description="Description optionnelle")
    image: Optional[str] = Field(None, description="URL de l'image / icône")
    order: int = Field(default=0, description="Ordre d'affichage dans la section")
    is_active: bool = Field(default=True, description="Sous-catégorie active")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)

    class Settings:
        name = "section_categories"
        indexes = ["section", "slug"]
