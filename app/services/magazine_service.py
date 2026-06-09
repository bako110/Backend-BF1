from app.models.magazine import Magazine
from app.schemas.magazine import MagazineCreate, MagazineUpdate, MagazineOut
from typing import List, Optional
from datetime import datetime


async def create_magazine(data: MagazineCreate) -> MagazineOut:
	magazine = Magazine(**data.dict())
	await magazine.insert()
	return MagazineOut.from_orm(magazine)


async def get_magazine(magazine_id: str) -> Optional[MagazineOut]:
	magazine = await Magazine.get(magazine_id)
	if magazine:
		return MagazineOut.from_orm(magazine)
	return None


async def list_magazine(skip: int = 0, limit: int = 50) -> List[MagazineOut]:
	magazines = await Magazine.find_all().skip(skip).limit(limit).to_list()
	return [MagazineOut.from_orm(magazine) for magazine in magazines]


async def update_magazine(magazine_id: str, data: MagazineUpdate) -> Optional[MagazineOut]:
	magazine = await Magazine.get(magazine_id)
	if not magazine:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(magazine, field, value)

	magazine.updated_at = datetime.utcnow()
	await magazine.save()
	return MagazineOut.from_orm(magazine)


async def delete_magazine(magazine_id: str) -> bool:
	magazine = await Magazine.get(magazine_id)
	if not magazine:
		return False
	await magazine.delete()
	return True
