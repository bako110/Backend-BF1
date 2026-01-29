from app.models.movie import Movie
from app.models.like import Like
from app.models.comment import Comment
from app.schemas.movie import MovieCreate, MovieUpdate
from typing import List, Optional, Dict
from datetime import datetime

async def create_movie(data: MovieCreate) -> Movie:
	movie = Movie(**data.dict())
	await movie.insert()
	return movie

async def get_movie(movie_id: str) -> Optional[Movie]:
	return await Movie.get(movie_id)

async def get_movie_with_stats(movie_id: str) -> Optional[Dict]:
	"""Récupérer un film avec statistiques de likes/comments"""
	movie = await Movie.get(movie_id)
	if not movie:
		return None
	
	# Compter les likes et comments
	likes_count = await Like.find(
		Like.content_id == movie_id,
		Like.content_type == "movie"
	).count()
	
	comments_count = await Comment.find(
		Comment.content_id == movie_id,
		Comment.content_type == "movie"
	).count()
	
	movie_dict = movie.dict()
	movie_dict['likes_count'] = likes_count
	movie_dict['comments_count'] = comments_count
	return movie_dict

async def list_movies(skip: int = 0, limit: int = 50, is_premium: Optional[bool] = None) -> List[Movie]:
	"""Lister les films avec pagination et filtre premium"""
	query = Movie.find_all()
	if is_premium is not None:
		query = Movie.find(Movie.is_premium == is_premium)
	return await query.skip(skip).limit(limit).to_list()

async def list_movies_by_genre(genre: str, skip: int = 0, limit: int = 50) -> List[Movie]:
	"""Lister les films par genre"""
	return await Movie.find(Movie.genre == genre).skip(skip).limit(limit).to_list()

async def update_movie(movie_id: str, data: MovieUpdate) -> Optional[Movie]:
	movie = await Movie.get(movie_id)
	if not movie:
		return None
	
	# Mise à jour partielle
	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(movie, field, value)
	
	movie.updated_at = datetime.utcnow()
	await movie.save()
	return movie

async def delete_movie(movie_id: str) -> bool:
	movie = await Movie.get(movie_id)
	if not movie:
		return False
	await movie.delete()
	return True
