from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_optional_user
from app.schemas.share import ShareCreate, ShareOut
from app.services.share_service import create_share, list_shares, count_shares, get_user_shares, delete_share
from typing import List

router = APIRouter()


@router.post("/", response_model=ShareOut)
async def add_share(data: ShareCreate, current_user=Depends(get_current_user)):
    share = await create_share(str(current_user.id), data)
    if not share:
        raise HTTPException(status_code=404, detail="Content not found")
    return share


@router.get("/content/{content_type}/{content_id}", response_model=List[ShareOut])
async def get_shares(content_type: str, content_id: str, skip: int = 0, limit: int = 100, current_user=Depends(get_optional_user)):
    return await list_shares(content_id, content_type, skip, limit)


@router.get("/content/{content_type}/{content_id}/count")
async def get_shares_count(content_type: str, content_id: str):
    count = await count_shares(content_id, content_type)
    return {"count": count}


@router.get("/me", response_model=List[ShareOut])
async def my_shares(skip: int = 0, limit: int = 100, current_user=Depends(get_current_user)):
    return await get_user_shares(str(current_user.id), skip, limit)


@router.delete("/{share_id}")
async def remove_share(share_id: str, current_user=Depends(get_current_user)):
    is_admin = getattr(current_user, "is_admin", False)
    ok = await delete_share(share_id, str(current_user.id), is_admin)
    if not ok:
        raise HTTPException(status_code=404, detail="Share not found or unauthorized")
    return {"ok": True}