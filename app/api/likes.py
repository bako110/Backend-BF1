from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.like import LikeCreate
from app.services.like_service import toggle_like, get_likes, count_likes, check_user_liked, remove_like, get_all_likes
from typing import List, Dict

router = APIRouter()

@router.get("/")
async def list_all_likes(current_user=Depends(get_admin_user), skip: int = 0, limit: int = 1000):
    """Lister tous les likes (admin seulement)"""
    return await get_all_likes(skip, limit)

@router.post("/toggle")
async def toggle_like_api(like: LikeCreate, current_user=Depends(get_current_user)):
    """Toggle like (ajouter ou retirer)"""
    try:
        result = await toggle_like(str(current_user.id), like)
        return result
    except Exception as e:
        print(f"❌ Erreur toggle like: {str(e)}")
        print(f"User ID: {current_user.id}, Content ID: {like.content_id}, Type: {like.content_type}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du toggle like: {str(e)}")

@router.get("/content/{content_type}/{content_id}")
async def list_likes(content_id: str, content_type: str, skip: int = 0, limit: int = 100):
    """Lister les likes d'un contenu avec infos utilisateur"""
    return await get_likes(content_id, content_type, skip, limit)

@router.get("/content/{content_type}/{content_id}/count")
async def count_likes_api(content_id: str, content_type: str):
    """Compter les likes d'un contenu"""
    count = await count_likes(content_id, content_type)
    return {"count": count}

@router.get("/check/{content_type}/{content_id}")
async def check_liked(content_id: str, content_type: str, current_user=Depends(get_current_user)):
    """Vérifier si l'utilisateur a liké ce contenu"""
    liked = await check_user_liked(str(current_user.id), content_id, content_type)
    return {"liked": liked}

@router.delete("/{like_id}")
async def remove_like_api(like_id: str, current_user=Depends(get_current_user)):
    """Supprimer un like par ID"""
    ok = await remove_like(like_id, str(current_user.id))
    if not ok:
        raise HTTPException(status_code=404, detail="Like not found or unauthorized")
    return {"ok": True}
