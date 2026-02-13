from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId


class CategoryBase(BaseModel):
    name: str = Field(..., description="Nom de la catégorie")
    description: Optional[str] = Field(None, description="Description de la catégorie")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nom de la catégorie")
    description: Optional[str] = Field(None, description="Description de la catégorie")


class CategoryResponse(CategoryBase):
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
