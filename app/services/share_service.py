from app.models.share import Share
from app.models.movie import Movie
from app.models.show import Show
from app.models.breakingNews import BreakingNews
from app.models.interview import Interview
from app.models.reel import Reel
from app.models.replay import Replay
from app.models.trendingShow import TrendingShow
from app.models.popularPrograms import PopularPrograms
from app.schemas.share import ShareCreate
from typing import List, Optional
from app.utils.engagement import increment_share


CONTENT_MODELS = {
    "movie": Movie,
    "show": Show,
    "breaking_news": BreakingNews,
    "interview": Interview,
    "reel": Reel,
    "replay": Replay,
    "trending_show": TrendingShow,
    "popular_program": PopularPrograms
}


async def _get_content(content_type: str, content_id: str):
    model = CONTENT_MODELS.get(content_type)
    if not model:
        return None
    return await model.get(content_id)


async def create_share(user_id: str, data: ShareCreate) -> Optional[Share]:
    content = await _get_content(data.content_type, data.content_id)
    if not content:
        return None

    share = Share(
        user_id=user_id,
        content_id=data.content_id,
        content_type=data.content_type,
        platform=data.platform,
        message=data.message
    )
    await share.insert()
    await increment_share(data.content_type, data.content_id, 1)
    return share


async def list_shares(content_id: str, content_type: str, skip: int = 0, limit: int = 100) -> List[Share]:
    return await Share.find(
        Share.content_id == content_id,
        Share.content_type == content_type
    ).sort(-Share.created_at).skip(skip).limit(limit).to_list()


async def count_shares(content_id: str, content_type: str) -> int:
    return await Share.find(
        Share.content_id == content_id,
        Share.content_type == content_type
    ).count()


async def get_user_shares(user_id: str, skip: int = 0, limit: int = 100) -> List[Share]:
    return await Share.find(Share.user_id == user_id).sort(-Share.created_at).skip(skip).limit(limit).to_list()


async def delete_share(share_id: str, user_id: str, is_admin: bool = False) -> bool:
    share = await Share.get(share_id)
    if not share:
        return False
    if share.user_id != user_id and not is_admin:
        return False
    content_id = share.content_id
    content_type = share.content_type
    await share.delete()
    await increment_share(content_type, content_id, -1)
    return True