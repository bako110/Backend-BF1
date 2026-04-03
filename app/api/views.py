"""
API pour gérer les vues des contenus.
Logique anti-doublon : 1 vue par utilisateur/IP par contenu toutes les 24h.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.models.show import Show
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.divertissement import Divertissement
from app.models.archive import Archive
from app.models.movie import Movie
from app.models.reel import Reel
from app.models.sport import Sport

router = APIRouter()

# Cache en mémoire : clé = "ip:content_type:content_id", valeur = datetime de la dernière vue
# TTL : 24h — même logique que YouTube/Facebook
_view_cache: dict[str, datetime] = {}
_VIEW_TTL = timedelta(hours=24)

MODEL_MAP = {
    'show': Show,
    'reportage': Reportage,
    'divertissement': Divertissement,
    'archive': Archive,
    'jtandmag': JTandMag,
    'movie': Movie,
    'reel': Reel,
    'sport': Sport,
    'sports': Sport,
}


def _get_viewer_id(request: Request, user_id: Optional[str]) -> str:
    """Identifiant unique du spectateur : user_id si connecté, sinon IP."""
    if user_id:
        return f"user:{user_id}"
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    return f"ip:{ip.split(',')[0].strip()}"


def _already_viewed(viewer_id: str, content_type: str, content_id: str) -> bool:
    """Retourne True si ce spectateur a déjà vu ce contenu dans les 24h."""
    key = f"{viewer_id}:{content_type}:{content_id}"
    last = _view_cache.get(key)
    if last and datetime.utcnow() - last < _VIEW_TTL:
        return True
    return False


def _mark_viewed(viewer_id: str, content_type: str, content_id: str):
    key = f"{viewer_id}:{content_type}:{content_id}"
    _view_cache[key] = datetime.utcnow()
    # Nettoyage périodique pour éviter la fuite mémoire
    if len(_view_cache) > 50_000:
        cutoff = datetime.utcnow() - _VIEW_TTL
        expired = [k for k, v in _view_cache.items() if v < cutoff]
        for k in expired:
            del _view_cache[k]


class ViewRequest(BaseModel):
    content_id: str
    content_type: str
    user_id: Optional[str] = None


@router.post("/increment")
async def increment_view(view_request: ViewRequest, request: Request):
    """
    Incrémenter les vues d'un contenu.
    Ignoré si le même utilisateur/IP a déjà vu dans les 24h.
    """
    content_id   = view_request.content_id
    content_type = view_request.content_type

    if content_type not in MODEL_MAP:
        raise HTTPException(status_code=400, detail=f"Type invalide: {content_type}")

    viewer_id = _get_viewer_id(request, view_request.user_id)

    # Déjà vu → on retourne le compteur actuel sans incrémenter
    if _already_viewed(viewer_id, content_type, content_id):
        Model = MODEL_MAP[content_type]
        content = await Model.get(content_id)
        return {
            "success": True,
            "already_counted": True,
            "content_id": content_id,
            "content_type": content_type,
            "views": content.views or 0 if content else 0,
        }

    Model = MODEL_MAP[content_type]
    content = await Model.get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail=f"{content_type} non trouvé")

    content.views = (content.views or 0) + 1
    await content.save()
    _mark_viewed(viewer_id, content_type, content_id)

    return {
        "success": True,
        "already_counted": False,
        "content_id": content_id,
        "content_type": content_type,
        "views": content.views,
    }


@router.get("/{content_type}/{content_id}")
async def get_views(content_type: str, content_id: str):
    """Récupérer le nombre de vues d'un contenu."""
    if content_type not in MODEL_MAP:
        raise HTTPException(status_code=400, detail=f"Type invalide: {content_type}")

    content = await MODEL_MAP[content_type].get(content_id)
    if not content:
        raise HTTPException(status_code=404, detail=f"{content_type} non trouvé")

    return {
        "content_id": content_id,
        "content_type": content_type,
        "views": content.views or 0,
    }
