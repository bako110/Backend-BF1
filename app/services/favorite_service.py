from app.models.favorite import Favorite
from app.models.movie import Movie
from app.models.show import Show
from app.schemas.favorite import FavoriteCreate
from typing import List, Optional, Dict

async def add_favorite(user_id: str, data: FavoriteCreate) -> Optional[Dict]:
	"""Ajouter un favori avec vérification des doublons"""
	# Vérifier que le contenu existe
	if data.movie_id:
		content = await Movie.get(data.movie_id)
		content_type = "movie"
		content_id = data.movie_id
	else:
		content = await Show.get(data.show_id)
		content_type = "show"
		content_id = data.show_id
	
	if not content:
		return None
	
	# Vérifier si déjà en favoris
	existing = await Favorite.find_one(
		Favorite.user_id == user_id,
		Favorite.movie_id == data.movie_id if data.movie_id else Favorite.show_id == data.show_id
	)
	
	if existing:
		return {"success": False, "message": "Déjà en favoris"}
	
	fav = Favorite(
		user_id=user_id,
		movie_id=data.movie_id,
		show_id=data.show_id
	)
	await fav.insert()
	
	return {
		"success": True,
		"message": "Ajouté aux favoris",
		"favorite_id": str(fav.id),
		"content_type": content_type
	}

async def get_favorite(fav_id: str) -> Optional[Favorite]:
	return await Favorite.get(fav_id)

async def list_favorites(user_id: str) -> List[Dict]:
	"""Lister les favoris avec enrichissement du contenu"""
	favorites = await Favorite.find(Favorite.user_id == user_id).to_list()
	
	enriched_favorites = []
	for fav in favorites:
		fav_dict = fav.dict()
		
		# Enrichir avec les infos du contenu
		if fav.movie_id:
			movie = await Movie.get(fav.movie_id)
			if movie:
				fav_dict['content_title'] = movie.title
				fav_dict['content_type'] = 'movie'
				fav_dict['image_url'] = movie.image_url
		elif fav.show_id:
			show = await Show.get(fav.show_id)
			if show:
				fav_dict['content_title'] = show.title
				fav_dict['content_type'] = 'show'
				fav_dict['image_url'] = show.image_url
		
		enriched_favorites.append(fav_dict)
	
	return enriched_favorites

async def remove_favorite(fav_id: str, user_id: str) -> bool:
	"""Supprimer un favori (seulement par le propriétaire)"""
	fav = await Favorite.get(fav_id)
	if not fav or fav.user_id != user_id:
		return False
	await fav.delete()
	return True

async def remove_favorite_by_content(user_id: str, content_id: str, content_type: str) -> bool:
	"""Supprimer un favori par contenu"""
	if content_type == "movie":
		fav = await Favorite.find_one(
			Favorite.user_id == user_id,
			Favorite.movie_id == content_id
		)
	else:
		fav = await Favorite.find_one(
			Favorite.user_id == user_id,
			Favorite.show_id == content_id
		)
	
	if not fav:
		return False
	
	await fav.delete()
	return True

async def get_all_favorites(skip: int = 0, limit: int = 1000) -> List[Dict]:
	"""Récupérer tous les favoris (pour admin)"""
	favorites = await Favorite.find().skip(skip).limit(limit).to_list()
	return [fav.dict() for fav in favorites]
