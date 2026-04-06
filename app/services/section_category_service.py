from app.models.section_category import SectionCategory
from app.schemas.section_category import SectionCategoryCreate, SectionCategoryUpdate, _slugify
from typing import List, Optional
from datetime import datetime


async def create_section_category(data: SectionCategoryCreate) -> SectionCategory:
    slug = _slugify(f"{data.section}-{data.name}")
    # Unicité section + name
    existing = await SectionCategory.find_one(
        SectionCategory.section == data.section,
        SectionCategory.name == data.name,
    )
    if existing:
        raise ValueError(f"Une sous-catégorie '{data.name}' existe déjà dans la section '{data.section}'")

    item = SectionCategory(**data.dict(), slug=slug)
    await item.insert()
    return item


async def list_section_categories(
    section: Optional[str] = None,
    active_only: bool = True,
) -> List[SectionCategory]:
    query = {}
    if section:
        query["section"] = section
    if active_only:
        query["is_active"] = True
    return await SectionCategory.find(query).sort("+order").to_list()


async def get_section_category(item_id: str) -> Optional[SectionCategory]:
    return await SectionCategory.get(item_id)


async def update_section_category(
    item_id: str, data: SectionCategoryUpdate
) -> Optional[SectionCategory]:
    item = await SectionCategory.get(item_id)
    if not item:
        return None
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    if "name" in update_data:
        item.slug = _slugify(f"{item.section}-{item.name}")
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def delete_section_category(item_id: str) -> bool:
    item = await SectionCategory.get(item_id)
    if not item:
        return False
    await item.delete()
    return True


async def get_sections_summary() -> dict:
    """Retourne toutes les sections avec leurs sous-catégories actives groupées."""
    all_cats = await SectionCategory.find({"is_active": True}).sort("+order").to_list()
    grouped: dict = {}
    for cat in all_cats:
        grouped.setdefault(cat.section, []).append(cat)
    return grouped
