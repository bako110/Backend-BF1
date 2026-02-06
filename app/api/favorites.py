from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.favorite import FavoriteCreate
from app.services.favorite_service import (
    add_favorite, get_favorite, list_favorites, 
    remove_favorite, remove_favorite_by_content, get_all_favorites
)
from typing import List

router = APIRouter()

@router.get("/")
async def list_all_favorites(current_user=Depends(get_admin_user), skip: int = 0, limit: int = 1000):
	"""Lister tous les favoris (admin seulement)"""
	return await get_all_favorites(skip, limit)

@router.post("/")
async def add_fav(fav: FavoriteCreate, current_user=Depends(get_current_user)):
	"""Ajouter un favori avec vérification des doublons"""
	result = await add_favorite(str(current_user.id), fav)
	if not result:
		raise HTTPException(status_code=404, detail="Content not found")
	if not result.get("success"):
		raise HTTPException(status_code=400, detail=result.get("message"))
	return result

@router.get("/me")
async def get_my_favorites(current_user=Depends(get_current_user)):
	"""Récupérer mes favoris avec enrichissement du contenu"""
	return await list_favorites(str(current_user.id))

@router.get("/user/{user_id}")
async def get_user_favs(user_id: str, current_user=Depends(get_current_user)):
	"""Récupérer les favoris d'un utilisateur"""
	return await list_favorites(user_id)

@router.get("/{fav_id}")
async def get_one_fav(fav_id: str, current_user=Depends(get_current_user)):
	"""Récupérer un favori par ID"""
	fav = await get_favorite(fav_id)
	if not fav:
		raise HTTPException(status_code=404, detail="Favorite not found")
	return fav

@router.delete("/{fav_id}")
async def delete_fav(fav_id: str, current_user=Depends(get_current_user)):
	"""Supprimer un favori par ID"""
	deleted = await remove_favorite(fav_id, str(current_user.id))
	if not deleted:
		raise HTTPException(status_code=404, detail="Favorite not found or unauthorized")
	return {"ok": True}

@router.delete("/content/{content_type}/{content_id}")
async def delete_fav_by_content(content_type: str, content_id: str, current_user=Depends(get_current_user)):
	"""Supprimer un favori par contenu"""
	deleted = await remove_favorite_by_content(str(current_user.id), content_id, content_type)
	if not deleted:
		raise HTTPException(status_code=404, detail="Favorite not found")
	return {"ok": True}
