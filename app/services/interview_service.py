from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewUpdate
from typing import List, Optional
from datetime import datetime


async def create_interview(data: InterviewCreate) -> Interview:
	interview = Interview(**data.dict())
	await interview.insert()
	return interview


async def get_interview(interview_id: str) -> Optional[Interview]:
	return await Interview.get(interview_id)


async def list_interviews(skip: int = 0, limit: int = 50) -> List[Interview]:
	return await Interview.find_all().sort(-Interview.created_at).skip(skip).limit(limit).to_list()


async def update_interview(interview_id: str, data: InterviewUpdate) -> Optional[Interview]:
	interview = await Interview.get(interview_id)
	if not interview:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(interview, field, value)

	interview.updated_at = datetime.utcnow()
	await interview.save()
	return interview


async def delete_interview(interview_id: str) -> bool:
	interview = await Interview.get(interview_id)
	if not interview:
		return False
	await interview.delete()
	return True
