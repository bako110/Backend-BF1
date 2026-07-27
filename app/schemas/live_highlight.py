from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LiveHighlightCreate(BaseModel):
    section: str
    title: str
    description: Optional[str] = None
    image_url: str
    video_url: Optional[str] = None
    event_date: datetime
    order: int = 0
    is_active: bool = True


class LiveHighlightImageUpdate(BaseModel):
    image_url: str


class LiveHighlightVideoUpdate(BaseModel):
    video_url: Optional[str] = None


class LiveHighlightUpdate(BaseModel):
    section: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class LiveHighlightOut(BaseModel):
    id: str
    section: str
    title: str
    description: Optional[str] = None
    image_url: str
    video_url: Optional[str] = None
    event_date: datetime
    order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @classmethod
    def from_doc(cls, doc) -> "LiveHighlightOut":
        return cls(
            id=str(doc.id),
            section=doc.section,
            title=doc.title,
            description=doc.description,
            image_url=doc.image_url,
            video_url=doc.video_url,
            event_date=doc.event_date,
            order=doc.order,
            is_active=doc.is_active,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
