"""
API des sous-catégories par section.

Sections disponibles :
  flash_infos      → Flash Infos
  jtandmag         → JT et Mag  (13h, 19h30, 7Infos, Surface de vérité, ...)
  reportage        → Reportages
  divertissement   → Divertissement et Mag  (LTS, Reem Wakato, Le Loft, ...)
  sport            → Sport
  tele_realite     → Télé Réalité et Événements  (Pépites d'entreprises, Marathon, ...)
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from app.utils.auth import get_admin_user, get_optional_user
from app.schemas.section_category import (
    SectionCategoryCreate, SectionCategoryUpdate, SectionCategoryOut,
    VALID_SECTIONS,
)
from app.services.section_category_service import (
    create_section_category, list_section_categories,
    get_section_category, update_section_category,
    delete_section_category, get_sections_summary,
)

router = APIRouter()


@router.get("/summary")
async def sections_summary(current_user=Depends(get_optional_user)):
    """
    Toutes les sections avec leurs sous-catégories actives groupées.
    Pratique pour charger les menus / filtres du frontend en un seul appel.
    """
    raw = await get_sections_summary()
    return {
        section: [
            {
                "id": str(cat.id),
                "name": cat.name,
                "slug": cat.slug,
                "image": cat.image,
                "order": cat.order,
            }
            for cat in cats
        ]
        for section, cats in raw.items()
    }


@router.get("/sections")
async def list_available_sections():
    """Liste les identifiants et libellés des grandes sections."""
    from app.models.section_category import SECTIONS
    return [{"key": k, "label": v} for k, v in SECTIONS.items()]


@router.post("", response_model=SectionCategoryOut)
async def create_cat(data: SectionCategoryCreate, current_user=Depends(get_admin_user)):
    """Créer une sous-catégorie dans une section (admin)."""
    try:
        return await create_section_category(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[SectionCategoryOut])
async def get_cats(
    section: Optional[str] = Query(
        None,
        description="Filtrer par section : flash_infos | jtandmag | reportage | divertissement | sport | tele_realite",
    ),
    active_only: bool = Query(True, description="N'afficher que les sous-catégories actives"),
    current_user=Depends(get_optional_user),
):
    """Lister les sous-catégories, avec filtre optionnel par section."""
    if section and section not in VALID_SECTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Section invalide. Valeurs : {', '.join(sorted(VALID_SECTIONS))}",
        )
    return await list_section_categories(section=section, active_only=active_only)


@router.get("/{cat_id}", response_model=SectionCategoryOut)
async def get_cat(cat_id: str, current_user=Depends(get_optional_user)):
    cat = await get_section_category(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Sous-catégorie non trouvée")
    return cat


@router.patch("/{cat_id}", response_model=SectionCategoryOut)
async def update_cat(
    cat_id: str, data: SectionCategoryUpdate, current_user=Depends(get_admin_user)
):
    updated = await update_section_category(cat_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Sous-catégorie non trouvée")
    return updated


@router.delete("/{cat_id}")
async def delete_cat(cat_id: str, current_user=Depends(get_admin_user)):
    deleted = await delete_section_category(cat_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sous-catégorie non trouvée")
    return {"ok": True}
