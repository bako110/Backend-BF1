from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class MessageBase(BaseModel):
    receiver_id: str = Field(..., description="ID du destinataire")
    subject: str = Field(..., min_length=1, max_length=200, description="Sujet")
    content: str = Field(..., min_length=1, description="Contenu du message")

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    is_read: Optional[bool] = None

class MessageOut(MessageBase):
    id: str
    sender_id: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    sender_username: Optional[str] = None
    receiver_username: Optional[str] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
