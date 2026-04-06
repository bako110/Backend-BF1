from app.models.tele_realite import TeleRealite
from app.schemas.tele_realite import TeleRealiteCreate, TeleRealiteUpdate
from typing import List, Optional
from datetime import datetime


async def create_tele_realite(data: TeleRealiteCreate) -> TeleRealite:
    item = TeleRealite(**data.dict())
    await item.insert()
    return item


async def get_tele_realite(item_id: str) -> Optional[TeleRealite]:
    return await TeleRealite.get(item_id)


async def list_tele_realite(
    skip: int = 0,
    limit: int = 20,
    sub_type: Optional[str] = None,
    search: Optional[str] = None,
) -> dict:
    query = {}
    if sub_type:
        query["sub_type"] = sub_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}},
        ]
    total = await TeleRealite.find(query).count()
    items = await TeleRealite.find(query).sort(-TeleRealite.created_at).skip(skip).limit(limit).to_list()
    return {"items": items, "total": total, "skip": skip, "limit": limit}


async def update_tele_realite(item_id: str, data: TeleRealiteUpdate) -> Optional[TeleRealite]:
    item = await TeleRealite.get(item_id)
    if not item:
        return None
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def delete_tele_realite(item_id: str) -> bool:
    item = await TeleRealite.get(item_id)
    if not item:
        return False
    await item.delete()
    return True
