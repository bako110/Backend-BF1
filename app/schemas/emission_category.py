from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class EmissionCategoryBase(BaseModel):
    name: str = Field(..., description="Nom de la catégorie d'émission")
    image_main: Optional[str] = Field(None, description="URL de l'image principale")
    image_background: Optional[str] = Field(None, description="URL de l'image de fond")
    image_icon: Optional[str] = Field(None, description="URL de l'icône")
    order: int = Field(default=0, description="Ordre d'affichage")
    is_active: bool = Field(default=True, description="Catégorie active ou non")


class EmissionCategoryCreate(EmissionCategoryBase):
    pass


class EmissionCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nom de la catégorie d'émission")
    image_main: Optional[str] = Field(None, description="URL de l'image principale")
    image_background: Optional[str] = Field(None, description="URL de l'image de fond")
    image_icon: Optional[str] = Field(None, description="URL de l'icône")
    order: Optional[int] = Field(None, description="Ordre d'affichage")
    is_active: Optional[bool] = Field(None, description="Catégorie active ou non")


class EmissionCategoryResponse(EmissionCategoryBase):
    id: str = Field(..., description="ID de la catégorie")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: Optional[datetime] = Field(None, description="Date de mise à jour")

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
