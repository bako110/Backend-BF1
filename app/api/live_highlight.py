"""
API Live Highlights – sections "À ne pas manquer" et "Moments forts" du LiveScreen mobile
Routes publiques : GET /live-highlights
Routes admin      : POST, PUT, PATCH image/vidéo, DELETE
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel

from app.utils.auth import get_admin_user
from app.schemas.live_highlight import (
    LiveHighlightCreate, LiveHighlightUpdate, LiveHighlightOut,
    LiveHighlightImageUpdate, LiveHighlightVideoUpdate,
)
from app.services.live_highlight_service import (
    VALID_SECTIONS,
    create_highlight,
    get_highlights,
    get_highlight,
    update_highlight,
    update_highlight_image,
    update_highlight_video,
    delete_highlight,
)

router = APIRouter()


def _validate_section(section: str):
    if section not in VALID_SECTIONS:
        raise HTTPException(status_code=400, detail=f"Section invalide. Valeurs acceptées: {VALID_SECTIONS}")


# ─────────────────────────────────────────
# PUBLIC
# ─────────────────────────────────────────

@router.get("", response_model=List[LiveHighlightOut])
async def list_highlights_public(
    section: Optional[str] = Query(None, description="a_ne_pas_manquer | moments_forts"),
):
    """Retourne les mises en avant actives, triées par ordre (utilisé par l'app mobile)."""
    if section:
        _validate_section(section)
    items = await get_highlights(section=section, active_only=True)
    return [LiveHighlightOut.from_doc(i) for i in items]


@router.get("/{item_id}", response_model=LiveHighlightOut)
async def get_one_highlight(item_id: str):
    item = await get_highlight(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Mise en avant introuvable")
    return LiveHighlightOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Créer
# ─────────────────────────────────────────

@router.post("", response_model=LiveHighlightOut)
async def create_highlight_admin(
    data: LiveHighlightCreate,
    _admin=Depends(get_admin_user),
):
    """Créer une nouvelle mise en avant (admin). L'image doit être déjà uploadée (image_url fourni)."""
    _validate_section(data.section)
    item = await create_highlight(data)
    return LiveHighlightOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Lister tout (actif + inactif)
# ─────────────────────────────────────────

@router.get("/admin/all", response_model=List[LiveHighlightOut])
async def list_highlights_admin(
    section: Optional[str] = Query(None, description="a_ne_pas_manquer | moments_forts"),
    _admin=Depends(get_admin_user),
):
    """Lister toutes les mises en avant (actives + inactives) pour le panneau admin."""
    if section:
        _validate_section(section)
    items = await get_highlights(section=section, active_only=False)
    return [LiveHighlightOut.from_doc(i) for i in items]


# ─────────────────────────────────────────
# ADMIN – Modifier les métadonnées
# ─────────────────────────────────────────

@router.put("/{item_id}", response_model=LiveHighlightOut)
async def update_highlight_admin(
    item_id: str,
    data: LiveHighlightUpdate,
    _admin=Depends(get_admin_user),
):
    """Modifier titre / description / date / ordre / statut / section."""
    if data.section:
        _validate_section(data.section)
    item = await update_highlight(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Mise en avant introuvable")
    return LiveHighlightOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Changer l'affiche
# ─────────────────────────────────────────

@router.patch("/{item_id}/image", response_model=LiveHighlightOut)
async def replace_highlight_image(
    item_id: str,
    data: LiveHighlightImageUpdate,
    _admin=Depends(get_admin_user),
):
    item = await update_highlight_image(item_id, image_url=data.image_url)
    if not item:
        raise HTTPException(status_code=404, detail="Mise en avant introuvable")
    return LiveHighlightOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Changer/retirer la bande-annonce
# ─────────────────────────────────────────

@router.patch("/{item_id}/video", response_model=LiveHighlightOut)
async def replace_highlight_video(
    item_id: str,
    data: LiveHighlightVideoUpdate,
    _admin=Depends(get_admin_user),
):
    item = await update_highlight_video(item_id, video_url=data.video_url)
    if not item:
        raise HTTPException(status_code=404, detail="Mise en avant introuvable")
    return LiveHighlightOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Supprimer
# ─────────────────────────────────────────

@router.delete("/{item_id}")
async def delete_highlight_admin(item_id: str, _admin=Depends(get_admin_user)):
    deleted = await delete_highlight(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Mise en avant introuvable")
    return {"ok": True, "message": "Mise en avant supprimée"}


class BatchDeleteIds(BaseModel):
    ids: List[str]

@router.post("/delete-batch")
async def delete_batch_highlights(body: BatchDeleteIds, _admin=Depends(get_admin_user)):
    """Supprimer plusieurs mises en avant en lot (admin seulement)"""
    if not body.ids:
        raise HTTPException(status_code=400, detail="Aucun ID fourni")
    count = 0
    for item_id in body.ids:
        if await delete_highlight(item_id):
            count += 1
    return {"ok": True, "deleted": count}
