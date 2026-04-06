from typing import List, Optional
from datetime import datetime

from app.models.carousel import CarouselItem
from app.schemas.carousel import CarouselItemCreate, CarouselItemUpdate


async def create_carousel_item(
    data: CarouselItemCreate,
) -> CarouselItem:
    item = CarouselItem(
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        order=data.order,
        is_active=data.is_active,
    )
    await item.insert()
    return item


async def get_all_carousel_items(active_only: bool = False) -> List[CarouselItem]:
    query = {"is_active": True} if active_only else {}
    items = await CarouselItem.find(query).sort("+order").to_list()
    return items


async def get_carousel_item(item_id: str) -> Optional[CarouselItem]:
    return await CarouselItem.get(item_id)


async def update_carousel_item(
    item_id: str, data: CarouselItemUpdate
) -> Optional[CarouselItem]:
    item = await CarouselItem.get(item_id)
    if not item:
        return None
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def update_carousel_image(
    item_id: str,
    image_url: str,
) -> Optional[CarouselItem]:
    item = await CarouselItem.get(item_id)
    if not item:
        return None

    item.image_url = image_url
    item.updated_at = datetime.utcnow()
    await item.save()
    return item


async def delete_carousel_item(item_id: str) -> bool:
    item = await CarouselItem.get(item_id)
    if not item:
        return False

    # Supprimer l'image Cloudinary
    if item.cloudinary_public_id:
        try:
            import cloudinary.uploader
            cloudinary.uploader.destroy(item.cloudinary_public_id)
        except Exception as e:
            print(f"⚠️ Erreur suppression Cloudinary: {e}")

    await item.delete()
    return True
