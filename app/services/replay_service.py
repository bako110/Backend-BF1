from app.models.replay import Replay
from app.schemas.replay import ReplayCreate, ReplayUpdate
from typing import List, Optional
from datetime import datetime


async def create_replay(data: ReplayCreate) -> Replay:
	replay = Replay(**data.dict())
	await replay.insert()
	return replay


async def get_replay(replay_id: str) -> Optional[Replay]:
	return await Replay.get(replay_id)


async def list_replays(skip: int = 0, limit: int = 50) -> List[Replay]:
	return await Replay.find_all().sort(-Replay.created_at).skip(skip).limit(limit).to_list()


async def update_replay(replay_id: str, data: ReplayUpdate) -> Optional[Replay]:
	replay = await Replay.get(replay_id)
	if not replay:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(replay, field, value)

	replay.updated_at = datetime.utcnow()
	await replay.save()
	return replay


async def delete_replay(replay_id: str) -> bool:
	replay = await Replay.get(replay_id)
	if not replay:
		return False
	await replay.delete()
	return True
