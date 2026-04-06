from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.jtandmag import JTandMagCreate, JTandMagUpdate, JTandMagOut
from app.services.jtandmag_service import (
	create_jtandmag, get_jtandmag, list_jtandmag, update_jtandmag, delete_jtandmag
)
from app.models.jtandmag import JTandMag

router = APIRouter()


@router.post("", response_model=JTandMagOut)
async def add_jtandmag(jtandmag: JTandMagCreate, current_user=Depends(get_admin_user)):
	return await create_jtandmag(jtandmag)


@router.get("")
async def get_all_jtandmag(
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

	total = await JTandMag.find(query).count()
	items = await JTandMag.find(query).skip(skip).limit(limit).to_list()

	return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{jtandmag_id}", response_model=JTandMagOut)
async def get_one_jtandmag(jtandmag_id: str, current_user=Depends(get_optional_user)):
	jtandmag = await get_jtandmag(jtandmag_id)
	if not jtandmag:
		raise HTTPException(status_code=404, detail="JT and Mag not found")
	return jtandmag


@router.put("/{jtandmag_id}", response_model=JTandMagOut)
async def update_one_jtandmag(jtandmag_id: str, jtandmag: JTandMagUpdate, current_user=Depends(get_admin_user)):
	updated_jtandmag = await update_jtandmag(jtandmag_id, jtandmag)
	if not updated_jtandmag:
		raise HTTPException(status_code=404, detail="JT and Mag not found")
	return updated_jtandmag


@router.delete("/{jtandmag_id}")
async def delete_one_jtandmag(jtandmag_id: str, current_user=Depends(get_admin_user)):
	success = await delete_jtandmag(jtandmag_id)
	if not success:
		raise HTTPException(status_code=404, detail="JT and Mag not found")
	return {"message": "JT and Mag deleted successfully"}
