from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

class FavoriteBase(BaseModel):
	show_id: Optional[str] = Field(None, description="ID de l'émission")
	movie_id: Optional[str] = Field(None, description="ID du film")

	@model_validator(mode='after')
	def check_one_content(self):
		show_id = self.show_id
		movie_id = self.movie_id
		if not show_id and not movie_id:
			raise ValueError('Au moins show_id ou movie_id doit être fourni')
		if show_id and movie_id:
			raise ValueError('Seulement show_id ou movie_id peut être fourni, pas les deux')
		return self

class FavoriteCreate(FavoriteBase):
	pass

class FavoriteOut(FavoriteBase):
	id: str
	user_id: str
	content_title: Optional[str] = Field(None, description="Titre du contenu")
	content_type: Optional[str] = Field(None, description="Type: movie ou show")
	added_at: datetime

	@validator("id", pre=True, always=True)
	def str_id(cls, v):
		if isinstance(v, ObjectId):
			return str(v)
		return v

	class Config:
		from_attributes = True
