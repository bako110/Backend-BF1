from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.divertissement import DivertissementCreate, DivertissementUpdate, DivertissementOut
from app.services.divertissement_service import (
	create_divertissement, get_divertissement, list_divertissement, update_divertissement, delete_divertissement
)

router = APIRouter()


@router.post("/", response_model=DivertissementOut)
async def add_divertissement(divertissement: DivertissementCreate, current_user=Depends(get_admin_user)):
	return await create_divertissement(divertissement)


@router.get("/", response_model=List[DivertissementOut])
async def get_all_divertissement(
	skip: int = 0, 
	limit: int = 50, 
	current_user=Depends(get_optional_user)
):
	return await list_divertissement(skip, limit)


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
