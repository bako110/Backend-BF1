from app.models.jtandmag import JTandMag
from app.schemas.jtandmag import JTandMagCreate, JTandMagUpdate, JTandMagOut
from typing import List, Optional
from datetime import datetime


async def create_jtandmag(data: JTandMagCreate) -> JTandMagOut:
	jtandmag = JTandMag(**data.dict())
	await jtandmag.insert()
	return JTandMagOut.from_orm(jtandmag)


async def get_jtandmag(jtandmag_id: str) -> Optional[JTandMagOut]:
	jtandmag = await JTandMag.get(jtandmag_id)
	if jtandmag:
		return JTandMagOut.from_orm(jtandmag)
	return None


async def list_jtandmag(skip: int = 0, limit: int = 50) -> List[JTandMagOut]:
	jtandmags = await JTandMag.find_all().skip(skip).limit(limit).to_list()
	return [JTandMagOut.from_orm(jtandmag) for jtandmag in jtandmags]


async def update_jtandmag(jtandmag_id: str, data: JTandMagUpdate) -> Optional[JTandMagOut]:
	jtandmag = await JTandMag.get(jtandmag_id)
	if not jtandmag:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(jtandmag, field, value)

	jtandmag.updated_at = datetime.utcnow()
	await jtandmag.save()
	return JTandMagOut.from_orm(jtandmag)


async def delete_jtandmag(jtandmag_id: str) -> bool:
	jtandmag = await JTandMag.get(jtandmag_id)
	if not jtandmag:
		return False
	await jtandmag.delete()
	return True
