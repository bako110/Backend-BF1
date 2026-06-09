from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.schemas.missed import MissedCreate, MissedUpdate, MissedResponse, MissedListResponse
from app.services.missed_service import missed_service
from app.utils.auth import get_current_user, get_optional_user

router = APIRouter()

@router.get("", response_model=MissedListResponse)
async def get_missed_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_user=Depends(get_optional_user)
):
    result = await missed_service.get_missed_list(skip=skip, limit=limit, is_active=is_active)
    return result

@router.get("/search", response_model=MissedListResponse)
async def search_missed(
    q: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_optional_user)
):
    result = await missed_service.search_missed(query=q, skip=skip, limit=limit)
    return result

@router.get("/category/{category}", response_model=MissedListResponse)
async def get_missed_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user=Depends(get_optional_user)
):
    result = await missed_service.get_missed_by_category(category=category, skip=skip, limit=limit)
    return result

@router.get("/{missed_id}", response_model=MissedResponse)
async def get_missed_by_id(
    missed_id: str,
    current_user=Depends(get_optional_user)
):
    missed = await missed_service.get_missed_by_id(missed_id)
    
    if not missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    await missed_service.increment_missed_views(missed_id)
    
    return missed

@router.post("", response_model=MissedResponse, status_code=201)
async def create_missed(
    missed_data: MissedCreate,
    current_user=Depends(get_current_user)
):
    created_missed = await missed_service.create_missed(missed_data)
    return created_missed

@router.put("/{missed_id}", response_model=MissedResponse)
async def update_missed(
    missed_id: str,
    missed_data: MissedUpdate,
    current_user=Depends(get_current_user)
):
    updated_missed = await missed_service.update_missed(missed_id, missed_data)
    
    if not updated_missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    return updated_missed

@router.delete("/{missed_id}", status_code=204)
async def delete_missed(
    missed_id: str,
    current_user=Depends(get_current_user)
):
    deleted = await missed_service.delete_missed(missed_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    return None

@router.post("/{missed_id}/increment-views", status_code=200)
async def increment_views(
    missed_id: str,
    current_user=Depends(get_optional_user)
):
    success = await missed_service.increment_missed_views(missed_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    return {"success": True, "message": "Vues incrémentées"}

# ─── Endpoints pour les interactions (commentaires, likes, favoris, shares) ───

@router.get("/{missed_id}/comments")
async def get_missed_comments(
    missed_id: str,
    current_user=Depends(get_optional_user)
):
    """Récupérer les commentaires d'un contenu manqué"""
    from app.models.comment import Comment
    
    missed = await missed_service.get_missed_by_id(missed_id)
    if not missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    comments = await Comment.find(
        Comment.content_type == "missed",
        Comment.content_id == missed_id
    ).sort("-created_at").to_list()
    
    return comments

@router.post("/{missed_id}/comments")
async def add_missed_comment(
    missed_id: str,
    text: str,
    current_user=Depends(get_current_user)
):
    """Ajouter un commentaire à un contenu manqué"""
    from app.models.comment import Comment
    
    missed = await missed_service.get_missed_by_id(missed_id)
    if not missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    if not missed.allow_comments:
        raise HTTPException(status_code=403, detail="Les commentaires sont désactivés pour ce contenu")
    
    comment = Comment(
        content_type="missed",
        content_id=missed_id,
        user_id=str(current_user.id),
        text=text
    )
    await comment.insert()
    
    return comment

@router.get("/{missed_id}/likes/count")
async def get_missed_likes_count(
    missed_id: str,
    current_user=Depends(get_optional_user)
):
    """Récupérer le nombre de likes d'un contenu manqué"""
    from app.models.like import Like
    
    count = await Like.find(
        Like.content_type == "missed",
        Like.content_id == missed_id
    ).count()
    
    return {"count": count}

@router.post("/{missed_id}/likes/toggle")
async def toggle_missed_like(
    missed_id: str,
    current_user=Depends(get_current_user)
):
    """Ajouter ou retirer un like sur un contenu manqué"""
    from app.models.like import Like
    
    missed = await missed_service.get_missed_by_id(missed_id)
    if not missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    existing_like = await Like.find_one(
        Like.content_type == "missed",
        Like.content_id == missed_id,
        Like.user_id == str(current_user.id)
    )
    
    if existing_like:
        await existing_like.delete()
        missed.likes = max(0, missed.likes - 1)
        await missed.save()
        return {"liked": False, "count": missed.likes}
    else:
        like = Like(
            content_type="missed",
            content_id=missed_id,
            user_id=str(current_user.id)
        )
        await like.insert()
        missed.likes += 1
        await missed.save()
        return {"liked": True, "count": missed.likes}

@router.get("/{missed_id}/likes/check")
async def check_missed_liked(
    missed_id: str,
    current_user=Depends(get_current_user)
):
    """Vérifier si l'utilisateur a liké ce contenu manqué"""
    from app.models.like import Like
    
    existing_like = await Like.find_one(
        Like.content_type == "missed",
        Like.content_id == missed_id,
        Like.user_id == str(current_user.id)
    )
    
    return {"liked": existing_like is not None}

@router.post("/{missed_id}/favorites")
async def add_missed_to_favorites(
    missed_id: str,
    current_user=Depends(get_current_user)
):
    """Ajouter un contenu manqué aux favoris"""
    from app.models.favorite import Favorite
    
    missed = await missed_service.get_missed_by_id(missed_id)
    if not missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    existing_fav = await Favorite.find_one(
        Favorite.content_type == "missed",
        Favorite.content_id == missed_id,
        Favorite.user_id == str(current_user.id)
    )
    
    if existing_fav:
        raise HTTPException(status_code=400, detail="Déjà dans les favoris")
    
    favorite = Favorite(
        content_type="missed",
        content_id=missed_id,
        user_id=str(current_user.id)
    )
    await favorite.insert()
    
    return {"success": True, "message": "Ajouté aux favoris"}

@router.delete("/{missed_id}/favorites")
async def remove_missed_from_favorites(
    missed_id: str,
    current_user=Depends(get_current_user)
):
    """Retirer un contenu manqué des favoris"""
    from app.models.favorite import Favorite
    
    existing_fav = await Favorite.find_one(
        Favorite.content_type == "missed",
        Favorite.content_id == missed_id,
        Favorite.user_id == str(current_user.id)
    )
    
    if not existing_fav:
        raise HTTPException(status_code=404, detail="Pas dans les favoris")
    
    await existing_fav.delete()
    
    return {"success": True, "message": "Retiré des favoris"}

@router.get("/{missed_id}/favorites/check")
async def check_missed_favorited(
    missed_id: str,
    current_user=Depends(get_current_user)
):
    """Vérifier si ce contenu manqué est dans les favoris"""
    from app.models.favorite import Favorite
    
    existing_fav = await Favorite.find_one(
        Favorite.content_type == "missed",
        Favorite.content_id == missed_id,
        Favorite.user_id == str(current_user.id)
    )
    
    return {"favorited": existing_fav is not None}

@router.post("/{missed_id}/share")
async def share_missed(
    missed_id: str,
    platform: str,
    current_user=Depends(get_optional_user)
):
    """Partager un contenu manqué"""
    from app.models.share import Share
    
    missed = await missed_service.get_missed_by_id(missed_id)
    if not missed:
        raise HTTPException(status_code=404, detail="Contenu manqué non trouvé")
    
    share = Share(
        content_type="missed",
        content_id=missed_id,
        user_id=str(current_user.id) if current_user else None,
        platform=platform
    )
    await share.insert()
    
    return {"success": True, "message": "Contenu partagé"}

@router.get("/{missed_id}/shares/count")
async def get_missed_shares_count(
    missed_id: str,
    current_user=Depends(get_optional_user)
):
    """Récupérer le nombre de partages d'un contenu manqué"""
    from app.models.share import Share
    
    count = await Share.find(
        Share.content_type == "missed",
        Share.content_id == missed_id
    ).count()
    
    return {"count": count}
