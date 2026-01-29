from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    username: str
    is_active: bool = True
    is_premium: bool = False
    favorites: List[str] = []

class UserCreate(UserBase):
    password: str

from pydantic import validator
from bson import ObjectId

class UserOut(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
class UserLoginSchema(BaseModel):
    identifier: str  # Peut être email, username ou phone
    password: str
