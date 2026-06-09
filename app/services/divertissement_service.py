from app.models.divertissement import Divertissement
from app.schemas.divertissement import DivertissementCreate, DivertissementUpdate
from typing import List, Optional
from datetime import datetime


async def create_divertissement(data: DivertissementCreate) -> Divertissement:
	divertissement = Divertissement(**data.dict())
	await divertissement.insert()
	return divertissement


async def get_divertissement(divertissement_id: str) -> Optional[Divertissement]:
	return await Divertissement.get(divertissement_id)


async def list_divertissement(skip: int = 0, limit: int = 50, category: Optional[str] = None) -> dict:
	query = {}
	if category:
		query["category"] = {"$regex": f"^{category}$", "$options": "i"}
	total = await Divertissement.find(query).count()
	items = await Divertissement.find(query).sort(-Divertissement.created_at).skip(skip).limit(limit).to_list()
	return {"items": items, "total": total, "skip": skip, "limit": limit}


async def update_divertissement(divertissement_id: str, data: DivertissementUpdate) -> Optional[Divertissement]:
	divertissement = await Divertissement.get(divertissement_id)
	if divertissement:
		update_data = data.dict(exclude_unset=True)
		for field, value in update_data.items():
			setattr(divertissement, field, value)

		divertissement.updated_at = datetime.utcnow()
		await divertissement.save()
	return divertissement


async def delete_divertissement(divertissement_id: str) -> bool:
	divertissement = await Divertissement.get(divertissement_id)
	if divertissement:
		await divertissement.delete()
		return True
	return False
