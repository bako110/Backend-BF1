from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
import re

VALID_SECTIONS = {
    "flash_infos",
    "jtandmag",
    "reportage",
    "divertissement",
    "sport",
    "tele_realite",
}


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[àáâãäå]", "a", value)
    value = re.sub(r"[èéêë]", "e", value)
    value = re.sub(r"[ìíîï]", "i", value)
    value = re.sub(r"[òóôõö]", "o", value)
    value = re.sub(r"[ùúûü]", "u", value)
    value = re.sub(r"[ç]", "c", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


class SectionCategoryBase(BaseModel):
    section: str = Field(
        ...,
        description="Grande section : flash_infos | jtandmag | reportage | divertissement | sport | tele_realite",
    )
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la sous-catégorie")
    description: Optional[str] = Field(None, max_length=500)
    image: Optional[str] = Field(None, description="URL image / icône")
    order: int = Field(default=0, ge=0, description="Ordre d'affichage")
    is_active: bool = Field(default=True)

    @validator("section")
    def validate_section(cls, v):
        if v not in VALID_SECTIONS:
            raise ValueError(
                f"Section invalide. Valeurs acceptées : {', '.join(sorted(VALID_SECTIONS))}"
            )
        return v

    @validator("image", pre=True)
    def empty_str_to_none(cls, v):
        return None if v == "" else v


class SectionCategoryCreate(SectionCategoryBase):
    pass


class SectionCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    image: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SectionCategoryOut(SectionCategoryBase):
    id: str
    slug: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
