from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional
from bson import ObjectId


class TrendingShowBase(BaseModel):
	title: str = Field(..., min_length=1, max_length=200, description="Titre de l'émission")
	category: str = Field(..., min_length=1, max_length=80, description="Catégorie")
	image: Optional[HttpUrl] = Field(None, description="Image de l'émission")
	video_url: Optional[str] = Field(None, description="URL de la vidéo (YouTube ou directe)")
	description: str = Field(..., min_length=1, max_length=5000, description="Description")
	host: str = Field(..., min_length=1, max_length=120, description="Animateur / présentateur")

	episodes: int = Field(..., ge=0, le=10000, description="Nombre d'épisodes")
	views: int = Field(default=0, ge=0, description="Nombre de vues")
	rating: float = Field(default=0, ge=0, le=5, description="Note (0 à 5)")

	@validator("image", pre=True)
	def empty_str_to_none(cls, v):
		if v == "" or v is None:
			return None
		return v


class TrendingShowCreate(TrendingShowBase):
	pass


class TrendingShowUpdate(BaseModel):
	title: Optional[str] = Field(None, min_length=1, max_length=200)
	category: Optional[str] = Field(None, min_length=1, max_length=80)
	image: Optional[HttpUrl] = None
	video_url: Optional[str] = None
	description: Optional[str] = Field(None, min_length=1, max_length=5000)
	host: Optional[str] = Field(None, min_length=1, max_length=120)

	episodes: Optional[int] = Field(None, ge=0, le=10000)
	views: Optional[int] = Field(None, ge=0)
	rating: Optional[float] = Field(None, ge=0, le=5)


class TrendingShowOut(TrendingShowBase):
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
