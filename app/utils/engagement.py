from bson import ObjectId

from app.models.movie import Movie
from app.models.breakingNews import BreakingNews
from app.models.divertissement import Divertissement
from app.models.reel import Reel
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.sport import Sport
from app.models.emission_category import EmissionCategory
from app.models.series import Series
from app.models.archive import Archive
from app.models.tele_realite import TeleRealite


CONTENT_MODELS = {
    "movie": Movie,
    "breaking_news": BreakingNews,
    "divertissement": Divertissement,
    "reel": Reel,
    "reportage": Reportage,
    "jtandmag": JTandMag,
    "sport": Sport,
    "emission_category": EmissionCategory,
    "series": Series,
    "archive": Archive,
    "tele_realite": TeleRealite,
    "event": TeleRealite,
}


async def _update_counter(content_type: str, content_id: str, field: str, delta: int) -> None:
    """Mise a jour atomique via $inc — evite les race conditions avec plusieurs workers."""
    model = CONTENT_MODELS.get(content_type)
    if not model:
        return
    try:
        col = model.get_motor_collection()
        # $max garantit que le champ ne descend pas sous 0
        pipeline = [{"$set": {field: {"$max": [0, {"$add": [{"$ifNull": [f"${field}", 0]}, delta]}]}}}]
        await col.update_one({"_id": ObjectId(content_id)}, pipeline)
    except Exception as e:
        print(f"[engagement] Erreur update {content_type}/{content_id} {field}: {e}")


async def increment_like(content_type: str, content_id: str, delta: int) -> None:
    await _update_counter(content_type, content_id, "likes", delta)


async def increment_comment(content_type: str, content_id: str, delta: int) -> None:
    await _update_counter(content_type, content_id, "comments", delta)


async def increment_share(content_type: str, content_id: str, delta: int) -> None:
    await _update_counter(content_type, content_id, "shares", delta)
