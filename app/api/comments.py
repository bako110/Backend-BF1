from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.comment import CommentCreate, CommentUpdate
from app.services.comment_service import (
    add_comment, get_comments, get_comment, update_comment, 
    delete_comment, count_comments, get_user_comments, get_all_comments
)
from typing import List

router = APIRouter()

@router.get("/")
async def list_all_comments(current_user=Depends(get_admin_user), skip: int = 0, limit: int = 1000):
    """Lister tous les commentaires (admin seulement)"""
    return await get_all_comments(skip, limit)

@router.post("/")
async def create_comment(comment: CommentCreate, current_user=Depends(get_current_user)):
    """Créer un commentaire"""
    result = await add_comment(str(current_user.id), comment)
    if not result:
        raise HTTPException(status_code=404, detail="Content not found")
    return result

@router.get("/content/{content_type}/{content_id}")
async def list_comments(content_id: str, content_type: str, skip: int = 0, limit: int = 50):
    """Lister les commentaires d'un contenu avec infos utilisateur"""
    return await get_comments(content_id, content_type, skip, limit)

@router.get("/content/{content_type}/{content_id}/count")
async def count_comments_api(content_id: str, content_type: str):
    """Compter les commentaires d'un contenu"""
    count = await count_comments(content_id, content_type)
    return {"count": count}

@router.get("/user/{user_id}")
async def get_user_comments_api(user_id: str, skip: int = 0, limit: int = 50):
    """Récupérer tous les commentaires d'un utilisateur"""
    return await get_user_comments(user_id, skip, limit)

@router.get("/{comment_id}")
async def get_one_comment(comment_id: str):
    """Récupérer un commentaire par ID"""
    comment = await get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/{comment_id}")
async def update_comment_api(comment_id: str, data: CommentUpdate, current_user=Depends(get_current_user)):
    """Mettre à jour un commentaire (seulement par l'auteur)"""
    updated = await update_comment(comment_id, str(current_user.id), data)
    if not updated:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
    return updated

@router.delete("/{comment_id}")
async def remove_comment(comment_id: str, current_user=Depends(get_current_user)):
    """Supprimer un commentaire (auteur ou admin)"""
    is_admin = getattr(current_user, "is_admin", False)
    ok = await delete_comment(comment_id, str(current_user.id), is_admin)
    if not ok:
        raise HTTPException(status_code=404, detail="Comment not found or unauthorized")
    return {"ok": True}
