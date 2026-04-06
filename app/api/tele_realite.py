from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.tele_realite import TeleRealiteCreate, TeleRealiteUpdate, TeleRealiteOut
from app.services.tele_realite_service import (
    create_tele_realite, get_tele_realite, list_tele_realite,
    update_tele_realite, delete_tele_realite,
)

router = APIRouter()


@router.post("", response_model=TeleRealiteOut)
async def add_tele_realite(data: TeleRealiteCreate, current_user=Depends(get_admin_user)):
    return await create_tele_realite(data)


@router.get("")
async def get_all_tele_realite(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    sub_type: Optional[str] = Query(None, description="Filtrer par type : tele_realite | event"),
    search: Optional[str] = Query(None, description="Recherche par titre, description, catégorie"),
    current_user=Depends(get_optional_user),
):
    return await list_tele_realite(skip=skip, limit=limit, sub_type=sub_type, search=search)


@router.get("/{item_id}", response_model=TeleRealiteOut)
async def get_one_tele_realite(item_id: str, current_user=Depends(get_optional_user)):
    item = await get_tele_realite(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    return item


@router.patch("/{item_id}", response_model=TeleRealiteOut)
async def update_one_tele_realite(
    item_id: str, data: TeleRealiteUpdate, current_user=Depends(get_admin_user)
):
    updated = await update_tele_realite(item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    return updated


@router.delete("/{item_id}")
async def delete_one_tele_realite(item_id: str, current_user=Depends(get_admin_user)):
    deleted = await delete_tele_realite(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    return {"ok": True}
