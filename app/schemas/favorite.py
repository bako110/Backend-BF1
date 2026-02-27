from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

ContentType = Literal[
	"movie",
	"show",
	"breaking_news",
	"reportage",
	"divertissement",
	"jtandmag",
	"popular_program",
	"archive",
	"program",
	"emission"
]


class FavoriteBase(BaseModel):
	content_id: str = Field(..., description="ID du contenu")
	content_type: ContentType = Field(..., description="Type de contenu")

class FavoriteCreate(FavoriteBase):
	pass

class FavoriteOut(FavoriteBase):
	id: str
	user_id: str
	content_title: Optional[str] = Field(None, description="Titre du contenu")
	added_at: datetime

	@validator("id", pre=True, always=True)
	def str_id(cls, v):
		if isinstance(v, ObjectId):
			return str(v)
		return v

	class Config:
		from_attributes = True
