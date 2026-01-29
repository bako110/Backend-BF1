from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class ShowBase(BaseModel):
	title: str = Field(..., min_length=1, max_length=200, description="Titre de l'émission")
	description: Optional[str] = Field(None, max_length=2000, description="Description")
	host: Optional[str] = Field(None, max_length=100, description="Animateur")
	duration: Optional[int] = Field(None, ge=0, le=600, description="Durée en minutes")
	category: Optional[str] = Field(None, max_length=50, description="Catégorie")
	edition: Optional[str] = Field(None, max_length=50, description="Édition")
	start_time: Optional[datetime] = Field(None, description="Heure de début")
	end_time: Optional[datetime] = Field(None, description="Heure de fin")
	image_url: Optional[str] = Field(None, description="URL de l'image")
	is_live: bool = Field(False, description="En direct")
	is_featured: bool = Field(False, description="Mise en avant")
	tags: List[str] = Field(default_factory=list, description="Tags")
	replay_url: Optional[str] = Field(None, description="URL du replay")
	live_url: Optional[str] = Field(None, description="URL du live")

class ShowCreate(ShowBase):
	pass

class ShowUpdate(BaseModel):
	title: Optional[str] = Field(None, min_length=1, max_length=200)
	description: Optional[str] = Field(None, max_length=2000)
	host: Optional[str] = None
	duration: Optional[int] = Field(None, ge=0, le=600)
	category: Optional[str] = None
	edition: Optional[str] = None
	start_time: Optional[datetime] = None
	end_time: Optional[datetime] = None
	image_url: Optional[str] = None
	is_live: Optional[bool] = None
	is_featured: Optional[bool] = None
	tags: Optional[List[str]] = None
	replay_url: Optional[str] = None
	live_url: Optional[str] = None

class ShowOut(ShowBase):
	id: str
	favorite_users: List[str] = Field(default_factory=list)
	likes_count: int = Field(0, description="Nombre de likes")
	comments_count: int = Field(0, description="Nombre de commentaires")
	created_at: datetime
	updated_at: Optional[datetime] = None

	@validator("id", pre=True, always=True)
	def str_id(cls, v):
		if isinstance(v, ObjectId):
			return str(v)
		return v

	class Config:
		from_attributes = True
