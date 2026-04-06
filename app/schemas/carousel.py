from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from bson import ObjectId


class CarouselItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    order: int = 0
    is_active: bool = True


class CarouselImageUpdate(BaseModel):
    image_url: str


class CarouselItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class CarouselItemOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    image_url: str
    order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_doc(cls, doc) -> "CarouselItemOut":
        return cls(
            id=str(doc.id),
            title=doc.title,
            description=doc.description,
            image_url=doc.image_url,
            order=doc.order,
            is_active=doc.is_active,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
