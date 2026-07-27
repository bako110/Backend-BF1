from typing import List, Optional
from datetime import datetime

from app.models.live_highlight import LiveHighlight
from app.schemas.live_highlight import LiveHighlightCreate, LiveHighlightUpdate

VALID_SECTIONS = ("a_ne_pas_manquer", "moments_forts")


async def create_highlight(data: LiveHighlightCreate) -> LiveHighlight:
    item = LiveHighlight(
        section=data.section,
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        video_url=data.video_url,
        event_date=data.event_date,
        order=data.order,
        is_active=data.is_active,
    )
    await item.insert()
    return item


async def get_highlights(
    section: Optional[str] = None,
    active_only: bool = False,
) -> List[LiveHighlight]:
    query = {}
    if section:
        query["section"] = section
    if active_only:
        query["is_active"] = True
    return await LiveHighlight.find(query).sort("+order").to_list()


async def get_highlight(item_id: str) -> Optional[LiveHighlight]:
    return await LiveHighlight.get(item_id)


async def update_highlight(item_id: str, data: LiveHighlightUpdate) -> Optional[LiveHighlight]:
    item = await LiveHighlight.get(item_id)
    if not item:
        return None
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def update_highlight_image(item_id: str, image_url: str) -> Optional[LiveHighlight]:
    item = await LiveHighlight.get(item_id)
    if not item:
        return None
    item.image_url = image_url
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def update_highlight_video(item_id: str, video_url: Optional[str]) -> Optional[LiveHighlight]:
    item = await LiveHighlight.get(item_id)
    if not item:
        return None
    item.video_url = video_url
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def delete_highlight(item_id: str) -> bool:
    item = await LiveHighlight.get(item_id)
    if not item:
        return False

    if item.file_public_id:
        try:
            from app.services.local_storage_service import local_storage
            local_storage.delete_file(item.file_public_id)
        except Exception as e:
            print(f"⚠️ Erreur suppression image locale: {e}")

    if item.video_public_id:
        try:
            from app.services.local_storage_service import local_storage
            local_storage.delete_file(item.video_public_id)
        except Exception as e:
            print(f"⚠️ Erreur suppression vidéo locale: {e}")

    await item.delete()
    return True
