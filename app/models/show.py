
from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class Show(Document):
	title: str = Field(..., description="Titre de l'émission")
	description: Optional[str] = Field(None, description="Description de l'émission")
	host: Optional[str] = Field(None, description="Nom de l'animateur")
	duration: Optional[int] = Field(None, description="Durée en minutes")
	category: Optional[str] = Field(None, description="Catégorie (info, culture, sport, etc.)")
	edition: Optional[str] = Field(None, description="Édition (Journal 13H30, 19H30, etc.)")
	start_time: Optional[datetime] = Field(None, description="Heure de début")
	end_time: Optional[datetime] = Field(None, description="Heure de fin")
	image_url: Optional[str] = Field(None, description="URL de l'image de l'émission")
	is_live: bool = Field(False, description="Statut en direct")
	live_url: Optional[str] = Field(None, description="URL du flux vidéo en direct")
	is_featured: bool = Field(False, description="Mise en avant sur la page d'accueil")
	tags: List[str] = Field(default_factory=list, description="Tags ou genres")
	favorite_users: List[str] = Field(default_factory=list, description="IDs des utilisateurs ayant mis en favori")
	# Les commentaires et likes sont gérés dans des collections séparées (Comment, Like)
	republished: bool = Field(False, description="Émission republiée ?")
	republished_at: Optional[datetime] = Field(None, description="Date de republication")
	replay_url: Optional[str] = Field(None, description="URL du replay si disponible")
	created_at: datetime = Field(default_factory=datetime.utcnow)
	updated_at: Optional[datetime] = None

	class Settings:
		name = "shows"
		indexes = [
			"category",
			"edition",
			"host",
			"is_live",
			"is_featured",
			"start_time",
			[("category", 1), ("is_live", -1)],
			[("edition", 1), ("start_time", -1)]
		]
