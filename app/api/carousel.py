"""
API Carousel – gestion des slides de la page d'accueil
Routes publiques  : GET /carousel, GET /carousel/{id}
Routes admin      : POST, PUT, PATCH image, DELETE
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.utils.auth import get_admin_user
from app.schemas.carousel import CarouselItemCreate, CarouselItemUpdate, CarouselItemOut, CarouselImageUpdate
from app.services.carousel_service import (
    create_carousel_item,
    get_all_carousel_items,
    get_carousel_item,
    update_carousel_item,
    update_carousel_image,
    delete_carousel_item,
)

router = APIRouter()


# ─────────────────────────────────────────
# PUBLIC
# ─────────────────────────────────────────

@router.get("", response_model=List[CarouselItemOut])
async def list_carousel_public():
    """Retourne les slides actives triées par ordre (utilisé par le frontend)."""
    items = await get_all_carousel_items(active_only=True)
    return [CarouselItemOut.from_doc(i) for i in items]


@router.get("/{item_id}", response_model=CarouselItemOut)
async def get_one_carousel(item_id: str):
    item = await get_carousel_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Slide introuvable")
    return CarouselItemOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Créer une slide avec image
# ─────────────────────────────────────────

@router.post("", response_model=CarouselItemOut)
async def create_carousel(
    data: CarouselItemCreate,
    _admin=Depends(get_admin_user),
):
    """Créer une nouvelle slide (admin). L'image doit être déjà uploadée (image_url fourni)."""
    item = await create_carousel_item(data)
    return CarouselItemOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Modifier les métadonnées
# ─────────────────────────────────────────

@router.put("/{item_id}", response_model=CarouselItemOut)
async def update_carousel(
    item_id: str,
    data: CarouselItemUpdate,
    _admin=Depends(get_admin_user),
):
    """Modifier titre / description / ordre / statut d'une slide."""
    item = await update_carousel_item(item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Slide introuvable")
    return CarouselItemOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Changer l'image d'une slide
# ─────────────────────────────────────────

@router.patch("/{item_id}/image", response_model=CarouselItemOut)
async def replace_carousel_image(
    item_id: str,
    data: CarouselImageUpdate,
    _admin=Depends(get_admin_user),
):
    """Remplacer l'image d'une slide existante (image déjà uploadée, image_url fourni)."""
    item = await update_carousel_image(item_id, image_url=data.image_url)
    if not item:
        raise HTTPException(status_code=404, detail="Slide introuvable")
    return CarouselItemOut.from_doc(item)


# ─────────────────────────────────────────
# ADMIN – Supprimer une slide
# ─────────────────────────────────────────

@router.delete("/{item_id}")
async def delete_carousel(item_id: str, _admin=Depends(get_admin_user)):
    """Supprimer une slide et son image Cloudinary."""
    deleted = await delete_carousel_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Slide introuvable")
    return {"ok": True, "message": "Slide supprimée"}


# ─────────────────────────────────────────
# ADMIN – Lister toutes les slides (y compris inactives)
# ─────────────────────────────────────────

@router.get("/admin/all", response_model=List[CarouselItemOut])
async def list_carousel_admin(_admin=Depends(get_admin_user)):
    """Lister toutes les slides (actives + inactives) pour le panneau admin."""
    items = await get_all_carousel_items(active_only=False)
    return [CarouselItemOut.from_doc(i) for i in items]
