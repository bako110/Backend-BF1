from app.models.reportage import Reportage
from app.schemas.reportage import ReportageCreate, ReportageUpdate
from typing import List, Optional
from datetime import datetime


async def create_reportage(data: ReportageCreate) -> Reportage:
	reportage = Reportage(**data.dict())
	await reportage.insert()
	return reportage


async def get_reportage(reportage_id: str) -> Optional[Reportage]:
	return await Reportage.get(reportage_id)


async def list_reportages(skip: int = 0, limit: int = 50, category: Optional[str] = None) -> dict:
	query = {}
	if category:
		query["category"] = {"$regex": f"^{category}$", "$options": "i"}
	total = await Reportage.find(query).count()
	items = await Reportage.find(query).sort(-Reportage.created_at).skip(skip).limit(limit).to_list()
	return {"items": items, "total": total, "skip": skip, "limit": limit}


async def update_reportage(reportage_id: str, data: ReportageUpdate) -> Optional[Reportage]:
	reportage = await Reportage.get(reportage_id)
	if reportage:
		update_data = data.dict(exclude_unset=True)
		for field, value in update_data.items():
			setattr(reportage, field, value)

		reportage.updated_at = datetime.utcnow()
		await reportage.save()
	return reportage


async def delete_reportage(reportage_id: str) -> bool:
	reportage = await Reportage.get(reportage_id)
	if reportage:
		await reportage.delete()
		return True
	return False
