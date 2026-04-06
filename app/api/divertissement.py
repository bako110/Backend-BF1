from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.divertissement import DivertissementCreate, DivertissementUpdate, DivertissementOut
from app.services.divertissement_service import (
	create_divertissement, get_divertissement, list_divertissement, update_divertissement, delete_divertissement
)
from app.models.divertissement import Divertissement

router = APIRouter()


@router.post("/", response_model=DivertissementOut)
async def add_divertissement(divertissement: DivertissementCreate, current_user=Depends(get_admin_user)):
	return await create_divertissement(divertissement)


@router.get("")
async def get_all_divertissement(
	skip: int = Query(0, ge=0),
	limit: int = Query(20, ge=1, le=500),
	search: Optional[str] = None,
	current_user=Depends(get_optional_user)
):
	query = {}
	if search:
		search_lower = search.strip()
		query["$or"] = [
			{"title": {"$regex": search_lower, "$options": "i"}},
			{"description": {"$regex": search_lower, "$options": "i"}},
			{"category": {"$regex": search_lower, "$options": "i"}},
			{"tags": {"$in": [search_lower]}},
		]

	total = await Divertissement.find(query).count()
	items = await Divertissement.find(query).sort(-Divertissement.created_at).skip(skip).limit(limit).to_list()

	return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{divertissement_id}", response_model=DivertissementOut)
async def get_one_divertissement(divertissement_id: str, current_user=Depends(get_optional_user)):
	divertissement = await get_divertissement(divertissement_id)
	if not divertissement:
		raise HTTPException(status_code=404, detail="Divertissement not found")
	return divertissement


@router.put("/{divertissement_id}", response_model=DivertissementOut)
async def update_one_divertissement(divertissement_id: str, divertissement: DivertissementUpdate, current_user=Depends(get_admin_user)):
	updated_divertissement = await update_divertissement(divertissement_id, divertissement)
	if not updated_divertissement:
		raise HTTPException(status_code=404, detail="Divertissement not found")
	return updated_divertissement


@router.delete("/{divertissement_id}")
async def delete_one_divertissement(divertissement_id: str, current_user=Depends(get_admin_user)):
	success = await delete_divertissement(divertissement_id)
	if not success:
		raise HTTPException(status_code=404, detail="Divertissement not found")
	return {"message": "Divertissement deleted successfully"}
