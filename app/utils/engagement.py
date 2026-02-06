from typing import Optional

from app.models.movie import Movie
from app.models.show import Show
from app.models.breakingNews import BreakingNews
from app.models.interview import Interview
from app.models.reel import Reel
from app.models.replay import Replay
from app.models.trendingShow import TrendingShow
from app.models.popularPrograms import PopularPrograms


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


async def _update_counter(content_type: str, content_id: str, field: str, delta: int) -> None:
    model = CONTENT_MODELS.get(content_type)
    if not model:
        return

    doc = await model.get(content_id)
    if not doc:
        return

    if not hasattr(doc, field):
        return

    current = getattr(doc, field) or 0
    new_value = current + delta
    if new_value < 0:
        new_value = 0
    setattr(doc, field, new_value)
    await doc.save()


async def increment_like(content_type: str, content_id: str, delta: int) -> None:
    await _update_counter(content_type, content_id, "likes", delta)


async def increment_comment(content_type: str, content_id: str, delta: int) -> None:
    await _update_counter(content_type, content_id, "comments", delta)


async def increment_share(content_type: str, content_id: str, delta: int) -> None:
    await _update_counter(content_type, content_id, "shares", delta)