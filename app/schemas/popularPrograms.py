from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class PopularProgramsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre du programme")
    schedule: str = Field(..., min_length=1, max_length=120, description="Horaire du programme")
    image: Optional[HttpUrl] = Field(None, description="Image de présentation")
    description: str = Field(..., min_length=1, max_length=5000, description="Description du programme")
    episodes: int = Field(..., ge=0, le=10000, description="Nombre d'épisodes disponibles")
    rating: float = Field(default=0, ge=0, le=5, description="Note moyenne du programme")
    category: str = Field(..., min_length=1, max_length=80, description="Catégorie du programme")

    @validator("image", pre=True)
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class PopularProgramsCreate(PopularProgramsBase):
    pass


class PopularProgramsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    schedule: Optional[str] = Field(None, min_length=1, max_length=120)
    image: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, min_length=1, max_length=5000)
    episodes: Optional[int] = Field(None, ge=0, le=10000)
    rating: Optional[float] = Field(None, ge=0, le=5)
    category: Optional[str] = Field(None, min_length=1, max_length=80)


class PopularProgramsOut(PopularProgramsBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
