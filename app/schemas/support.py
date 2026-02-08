from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from datetime import datetime

class SupportTicketBase(BaseModel):
    subject: str
    message: str
    category: str  # bug, feature, question, other
    priority: str = "normal"  # low, normal, high, urgent
    device_info: Optional[str] = None
    app_version: Optional[str] = None


class SupportTicketCreate(SupportTicketBase):
    pass


class SupportTicketUpdate(BaseModel):
    subject: Optional[str] = None
    message: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class SupportTicketResponse(BaseModel):
    message: str
    author: str  # admin or user
    created_at: datetime


class SupportTicketOut(SupportTicketBase):
    id: str
    user_id: str
    status: str
    responses: List[dict] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    @field_validator('id', 'user_id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class FAQBase(BaseModel):
    question: str
    answer: str
    category: str
    order: int = 0


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class FAQOut(FAQBase):
    id: str
    is_active: bool
    views: int
    helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
