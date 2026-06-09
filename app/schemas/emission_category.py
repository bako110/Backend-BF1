from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId
from urllib.parse import quote


VALID_SECTIONS = {
    "magazine", "jtandmag", "divertissement", "reportage",
    "tele_realite", "sport", "flash_infos"
}

SECTION_ENDPOINT_MAP = {
    "magazine": "/magazine",
    "jtandmag": "/jtandmag",
    "divertissement": "/divertissement",
    "reportage": "/reportage",
    "tele_realite": "/tele-realite",
    "sport": "/sport",
    "flash_infos": "/flash-infos",
}


def build_filter_path(section: Optional[str], name: str) -> Optional[str]:
    if not section or section not in SECTION_ENDPOINT_MAP:
        return None
    endpoint = SECTION_ENDPOINT_MAP[section]
    encoded_name = quote(name, safe="")
    return f"{endpoint}?skip=0&limit=20&category={encoded_name}"


class EmissionCategoryBase(BaseModel):
    name: str = Field(..., description="Nom de la catégorie d'émission")
    section: Optional[str] = Field(None, description="Section : magazine | jtandmag | divertissement | reportage | tele_realite | sport | flash_infos")
    image_main: Optional[str] = Field(None, description="URL de l'image principale")
    image_background: Optional[str] = Field(None, description="URL de l'image de fond")
    image_icon: Optional[str] = Field(None, description="URL de l'icône")
    order: int = Field(default=0, description="Ordre d'affichage")
    is_active: bool = Field(default=True, description="Catégorie active ou non")

    @validator("section")
    def validate_section(cls, v):
        if v is not None and v not in VALID_SECTIONS:
            raise ValueError(f"Section invalide. Valeurs acceptées : {', '.join(sorted(VALID_SECTIONS))}")
        return v


class EmissionCategoryCreate(EmissionCategoryBase):
    pass


class EmissionCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nom de la catégorie d'émission")
    section: Optional[str] = Field(None, description="Section : magazine | jtandmag | divertissement | reportage | tele_realite | sport | flash_infos")
    image_main: Optional[str] = Field(None, description="URL de l'image principale")
    image_background: Optional[str] = Field(None, description="URL de l'image de fond")
    image_icon: Optional[str] = Field(None, description="URL de l'icône")
    order: Optional[int] = Field(None, description="Ordre d'affichage")
    is_active: Optional[bool] = Field(None, description="Catégorie active ou non")

    @validator("section")
    def validate_section(cls, v):
        if v is not None and v not in VALID_SECTIONS:
            raise ValueError(f"Section invalide. Valeurs acceptées : {', '.join(sorted(VALID_SECTIONS))}")
        return v


class EmissionCategoryResponse(EmissionCategoryBase):
    id: str = Field(..., description="ID de la catégorie")
    filter_path: Optional[str] = Field(None, description="Chemin de filtre relatif (à préfixer par la base URL côté frontend)")
    is_new: bool = Field(default=False, description="Nouvelle catégorie")
    likes: int = Field(default=0, description="Nombre de likes")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
