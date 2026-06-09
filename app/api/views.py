"""
API pour gérer les vues des contenus.
- Incrément atomique via $inc (pas de race condition)
- Anti-doublon persisté en DB (ViewLog) — survit aux redémarrages
- TTL 24h par user_id (si connecté) ou IP (anonyme)
- Silencieux : ne plante jamais le serveur, retourne toujours une réponse
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
from bson import ObjectId

from app.models.view_log import ViewLog
from app.utils.engagement import CONTENT_MODELS, _update_counter

router = APIRouter()

_VIEW_TTL = timedelta(hours=24)

# Types acceptés (alias inclus)
_TYPE_ALIASES = {
    'sports': 'sport',
    'news':   'breaking_news',
    'event':  'tele_realite',
}


def _normalize_type(content_type: str) -> str:
    return _TYPE_ALIASES.get(content_type, content_type)


def _get_identifier(request: Request, user_id: Optional[str]) -> str:
    """user_id si connecté, sinon IP réelle (header x-forwarded-for pour proxy/Fly.io)."""
    if user_id:
        return f"u:{user_id}"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    elif request.client:
        ip = request.client.host
    else:
        ip = "unknown"
    return f"ip:{ip}"


async def _already_viewed_db(identifier: str, content_type: str, content_id: str) -> bool:
    """Vérifie en DB si une vue a déjà été comptée dans les 24h."""
    try:
        cutoff = datetime.now(timezone.utc) - _VIEW_TTL
        existing = await ViewLog.find_one(
            ViewLog.identifier   == identifier,
            ViewLog.content_type == content_type,
            ViewLog.content_id   == content_id,
            ViewLog.created_at   >= cutoff,
        )
        return existing is not None
    except Exception as e:
        print(f"[views] Erreur check ViewLog: {e}")
        return False  # En cas d'erreur DB, on laisse passer (ne pas bloquer)


async def _record_view_db(identifier: str, content_type: str, content_id: str) -> None:
    """Enregistre la vue en DB."""
    try:
        log = ViewLog(
            content_id   = content_id,
            content_type = content_type,
            identifier   = identifier,
        )
        await log.insert()
    except Exception as e:
        print(f"[views] Erreur insert ViewLog: {e}")


async def _get_current_views(content_type: str, content_id: str) -> int:
    """Récupère le compteur de vues actuel sans planter."""
    try:
        model = CONTENT_MODELS.get(content_type)
        if not model:
            return 0
        col = model.get_motor_collection()
        doc = await col.find_one({"_id": ObjectId(content_id)}, {"views": 1})
        return int(doc.get("views", 0)) if doc else 0
    except Exception:
        return 0


class ViewRequest(BaseModel):
    content_id:   str
    content_type: str
    user_id:      Optional[str] = None


@router.post("/increment")
async def increment_view(view_request: ViewRequest, request: Request):
    """
    Incrémenter les vues d'un contenu.
    - Atomique ($inc MongoDB)
    - Anti-doublon 24h persisté en DB
    - Ne renvoie jamais d'erreur 4xx/5xx au client (silencieux)
    """
    content_id   = (view_request.content_id or "").strip()
    content_type = _normalize_type((view_request.content_type or "").strip())

    # Type inconnu → on ignore silencieusement
    if content_type not in CONTENT_MODELS:
        return {"success": False, "reason": "unknown_type", "views": 0}

    # ID vide
    if not content_id:
        return {"success": False, "reason": "missing_id", "views": 0}

    identifier = _get_identifier(request, view_request.user_id)

    # Déjà vu dans les 24h → retourner le compteur sans incrémenter
    if await _already_viewed_db(identifier, content_type, content_id):
        views = await _get_current_views(content_type, content_id)
        return {
            "success":        True,
            "already_counted": True,
            "content_id":     content_id,
            "content_type":   content_type,
            "views":          views,
        }

    # Vérifier que le document existe avant d'incrémenter
    try:
        model = CONTENT_MODELS[content_type]
        col   = model.get_motor_collection()
        exists = await col.find_one({"_id": ObjectId(content_id)}, {"_id": 1})
        if not exists:
            return {"success": False, "reason": "not_found", "views": 0}
    except Exception as e:
        print(f"[views] Erreur find document {content_type}/{content_id}: {e}")
        return {"success": False, "reason": "db_error", "views": 0}

    # Incrément atomique
    await _update_counter(content_type, content_id, "views", 1)

    # Enregistrer la vue en DB (anti-doublon)
    await _record_view_db(identifier, content_type, content_id)

    views = await _get_current_views(content_type, content_id)

    return {
        "success":        True,
        "already_counted": False,
        "content_id":     content_id,
        "content_type":   content_type,
        "views":          views,
    }


@router.get("/{content_type}/{content_id}")
async def get_views(content_type: str, content_id: str):
    """Récupérer le nombre de vues d'un contenu."""
    content_type = _normalize_type(content_type)
    if content_type not in CONTENT_MODELS:
        return {"content_id": content_id, "content_type": content_type, "views": 0}
    views = await _get_current_views(content_type, content_id)
    return {"content_id": content_id, "content_type": content_type, "views": views}
