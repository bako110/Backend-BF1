from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class NotificationBase(BaseModel):
	title: str = Field(..., min_length=1, max_length=100, description="Titre")
	message: str = Field(..., min_length=1, max_length=500, description="Message")
	category: Optional[str] = Field(None, max_length=50, description="Catégorie")

class NotificationCreate(NotificationBase):
	user_id: Optional[str] = Field(None, description="ID utilisateur (None = broadcast)")

class NotificationOut(NotificationBase):
	id: str
	user_id: Optional[str] = None
	is_read: bool = False
	created_at: datetime

	@validator("id", pre=True, always=True)
	def str_id(cls, v):
		if isinstance(v, ObjectId):
			return str(v)
		return v

	class Config:
		from_attributes = True
