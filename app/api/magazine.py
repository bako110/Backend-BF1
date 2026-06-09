from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.magazine import MagazineCreate, MagazineUpdate, MagazineOut
from app.services.magazine_service import (
	create_magazine, get_magazine, list_magazine, update_magazine, delete_magazine
)
from app.models.magazine import Magazine

router = APIRouter()


@router.post("", response_model=MagazineOut)
async def add_magazine(magazine: MagazineCreate, current_user=Depends(get_admin_user)):
	return await create_magazine(magazine)


@router.get("")
async def get_all_magazine(
	skip: int = Query(0, ge=0),
	limit: int = Query(20, ge=1, le=500),
	category: Optional[str] = Query(None, description="Filtrer par catégorie : Surface de vérité | Le Loft | Au-delà de l'écorce | Leçons de vie | Émission spéciale"),
	search: Optional[str] = None,
	current_user=Depends(get_optional_user)
):
	query = {}
	if category:
		cat_clean = category.strip()
		query["category"] = {"$regex": f"^\\s*{cat_clean}\\s*$", "$options": "i"}
	if search:
		search_lower = search.strip()
		query["$or"] = [
			{"title": {"$regex": search_lower, "$options": "i"}},
			{"description": {"$regex": search_lower, "$options": "i"}},
			{"category": {"$regex": search_lower, "$options": "i"}},
		]

	total = await Magazine.find(query).count()
	items = await Magazine.find(query).sort("-created_at").skip(skip).limit(limit).to_list()

	return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get("/{magazine_id}", response_model=MagazineOut)
async def get_one_magazine(magazine_id: str, current_user=Depends(get_optional_user)):
	magazine = await get_magazine(magazine_id)
	if not magazine:
		raise HTTPException(status_code=404, detail="Magazine not found")
	return magazine


@router.put("/{magazine_id}", response_model=MagazineOut)
async def update_one_magazine(magazine_id: str, magazine: MagazineUpdate, current_user=Depends(get_admin_user)):
	updated_magazine = await update_magazine(magazine_id, magazine)
	if not updated_magazine:
		raise HTTPException(status_code=404, detail="Magazine not found")
	return updated_magazine


@router.delete("/{magazine_id}")
async def delete_one_magazine(magazine_id: str, current_user=Depends(get_admin_user)):
	success = await delete_magazine(magazine_id)
	if not success:
		raise HTTPException(status_code=404, detail="Magazine not found")
	return {"message": "Magazine deleted successfully"}


class BatchDeleteIds(BaseModel):
	ids: List[str]

@router.post("/delete-batch")
async def delete_batch_magazine(body: BatchDeleteIds, current_user=Depends(get_admin_user)):
	if not body.ids:
		raise HTTPException(status_code=400, detail="Aucun ID fourni")
	count = 0
	for item_id in body.ids:
		if await delete_magazine(item_id):
			count += 1
	return {"ok": True, "deleted": count}
