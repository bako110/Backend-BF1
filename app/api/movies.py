from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user, get_optional_user
from app.schemas.movie import MovieCreate, MovieOut, MovieUpdate
from app.services.movie_service import create_movie, get_movie, get_movie_with_stats, list_movies, update_movie, delete_movie
from typing import List

router = APIRouter()

@router.post("/", response_model=MovieOut)
async def add_movie(movie: MovieCreate, current_user=Depends(get_admin_user)):
	return await create_movie(movie)

@router.get("/")
async def get_all_movies(
	skip: int = 0, 
	limit: int = 50, 
	is_premium: bool = None,
	current_user=Depends(get_optional_user)
):
	"""Lister les films avec pagination et filtre premium"""
	return await list_movies(skip, limit, is_premium)

@router.get("/{movie_id}")
async def get_one_movie(movie_id: str, with_stats: bool = True, current_user=Depends(get_optional_user)):
	"""Récupérer un film avec ou sans statistiques"""
	if with_stats:
		movie = await get_movie_with_stats(movie_id)
	else:
		movie = await get_movie(movie_id)
	
	if not movie:
		raise HTTPException(status_code=404, detail="Movie not found")
	return movie

@router.patch("/{movie_id}")
async def update_one_movie(movie_id: str, movie: MovieUpdate, current_user=Depends(get_admin_user)):
	"""Mise à jour partielle d'un film (admin seulement)"""
	updated = await update_movie(movie_id, movie)
	if not updated:
		raise HTTPException(status_code=404, detail="Movie not found")
	return updated

@router.delete("/{movie_id}")
async def delete_one_movie(movie_id: str, current_user=Depends(get_current_user)):
	deleted = await delete_movie(movie_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Movie not found")
	return {"ok": True}
# Endpoints films
