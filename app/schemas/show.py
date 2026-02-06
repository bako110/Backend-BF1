from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class ShowBase(BaseModel):
	title: str = Field(..., min_length=1, max_length=200, description="Titre de l'émission")
	description: Optional[str] = Field(None, max_length=2000, description="Description")
	host: Optional[str] = Field(None, max_length=100, description="Animateur")
	category: Optional[str] = Field(None, max_length=50, description="Catégorie")

	image_url: Optional[HttpUrl] = Field(None, description="Image de l'émission")

	# Flux unique
	is_live: bool = Field(False, description="En direct ?")
	stream_url: Optional[HttpUrl] = Field(None, description="URL du flux unique (live ou replay)")

	# Replay
	is_replay: bool = Field(False, description="Disponible en replay ?")
	replay_at: Optional[datetime] = Field(None, description="Date de diffusion")

	# Engagement
	views: int = Field(0, ge=0, description="Nombre de vues")
	is_featured: bool = Field(False, description="Mise en avant")
	tags: List[str] = Field(default_factory=list, description="Tags")

class ShowCreate(ShowBase):
	pass

class ShowUpdate(BaseModel):
	title: Optional[str] = Field(None, min_length=1, max_length=200)
	description: Optional[str] = Field(None, max_length=2000)
	host: Optional[str] = Field(None, max_length=100)
	category: Optional[str] = Field(None, max_length=50)

	image_url: Optional[HttpUrl] = None

	is_live: Optional[bool] = None
	stream_url: Optional[HttpUrl] = None

	is_replay: Optional[bool] = None
	replay_at: Optional[datetime] = None

	views: Optional[int] = Field(None, ge=0)
	is_featured: Optional[bool] = None
	tags: Optional[List[str]] = None

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
