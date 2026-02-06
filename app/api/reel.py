from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel, Field
from app.utils.auth import get_admin_user, get_optional_user, get_current_user
from app.schemas.reel import ReelCreate, ReelUpdate, ReelOut
from app.schemas.comment import CommentCreate, CommentOut
from app.services.reel_service import create_reel, get_reel, list_reels, update_reel, delete_reel
from app.services import like_service, comment_service, share_service

router = APIRouter()


@router.post("/", response_model=ReelOut)
async def add_reel(reel: ReelCreate, current_user=Depends(get_admin_user)):
	return await create_reel(reel)


@router.get("/", response_model=List[ReelOut])
async def get_all_reels(
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	return await list_reels(skip, limit)


@router.get("/{reel_id}", response_model=ReelOut)
async def get_one_reel(reel_id: str, current_user=Depends(get_optional_user)):
	reel = await get_reel(reel_id)
	if not reel:
		raise HTTPException(status_code=404, detail="Reel not found")
	return reel


@router.patch("/{reel_id}", response_model=ReelOut)
async def update_one_reel(reel_id: str, data: ReelUpdate, current_user=Depends(get_admin_user)):
	updated = await update_reel(reel_id, data)
	if not updated:
		raise HTTPException(status_code=404, detail="Reel not found")
	return updated


@router.delete("/{reel_id}")
async def delete_one_reel(reel_id: str, current_user=Depends(get_admin_user)):
	deleted = await delete_reel(reel_id)
	if not deleted:
		raise HTTPException(status_code=404, detail="Reel not found")
	return {"ok": True}


# ==================== LIKES ====================

@router.post("/{reel_id}/like")
async def like_reel(reel_id: str, current_user=Depends(get_current_user)):
	"""Liker un reel"""
	try:
		from app.schemas.like import LikeCreate
		like_data = LikeCreate(
			content_id=reel_id,
			content_type="reel"
		)
		result = await like_service.toggle_like(
			user_id=str(current_user.id),
			data=like_data
		)
		return result
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{reel_id}/like")
async def unlike_reel(reel_id: str, current_user=Depends(get_current_user)):
	"""Retirer le like d'un reel"""
	try:
		from app.schemas.like import LikeCreate
		like_data = LikeCreate(
			content_id=reel_id,
			content_type="reel"
		)
		result = await like_service.toggle_like(
			user_id=str(current_user.id),
			data=like_data
		)
		return result
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{reel_id}/likes/count")
async def get_reel_likes_count(reel_id: str, current_user=Depends(get_optional_user)):
	"""Obtenir le nombre de likes d'un reel"""
	count = await like_service.count_likes(reel_id, "reel")
	return {"count": count}


# ==================== COMMENTS ====================

@router.get("/{reel_id}/comments", response_model=List[CommentOut])
async def get_reel_comments(
	reel_id: str,
	skip: int = 0,
	limit: int = 50,
	current_user=Depends(get_optional_user)
):
	"""Récupérer les commentaires d'un reel"""
	comments = await comment_service.get_comments(
		content_id=reel_id,
		content_type="reel",
		skip=skip,
		limit=limit
	)
	return comments


class CommentTextOnly(BaseModel):
	text: str = Field(..., min_length=1, max_length=1000)

@router.post("/{reel_id}/comments", response_model=CommentOut)
async def create_reel_comment(
	reel_id: str,
	comment_data: CommentTextOnly,
	current_user=Depends(get_current_user)
):
	"""Créer un commentaire sur un reel"""
	try:
		from app.schemas.comment import CommentCreate as CommentCreateSchema
		comment_create = CommentCreateSchema(
			content_id=reel_id,
			content_type="reel",
			text=comment_data.text
		)
		comment = await comment_service.add_comment(
			user_id=str(current_user.id),
			data=comment_create
		)
		if not comment:
			raise HTTPException(status_code=404, detail="Reel not found")
		return comment
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


# ==================== SHARES ====================

@router.post("/{reel_id}/share")
async def share_reel(reel_id: str, current_user=Depends(get_current_user)):
	"""Partager un reel"""
	try:
		from app.schemas.share import ShareCreate
		share_data = ShareCreate(
			content_id=reel_id,
			content_type="reel",
			platform="app",
			message=None
		)
		result = await share_service.create_share(
			user_id=str(current_user.id),
			data=share_data
		)
		if not result:
			raise HTTPException(status_code=404, detail="Reel not found")
		return {"success": True, "message": "Reel partagé avec succès"}
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{reel_id}/shares/count")
async def get_reel_shares_count(reel_id: str, current_user=Depends(get_optional_user)):
	"""Obtenir le nombre de partages d'un reel"""
	count = await share_service.count_shares(reel_id, "reel")
	return {"count": count}
