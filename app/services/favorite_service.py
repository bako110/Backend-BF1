from app.models.favorite import Favorite
from app.models.movie import Movie
from app.models.show import Show
from app.models.breakingNews import BreakingNews
from app.models.divertissement import Divertissement
from app.models.reel import Reel
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.popularPrograms import PopularPrograms
from app.models.sport import Sport
from app.models.emission_category import EmissionCategory
from app.models.series import Series
from app.schemas.favorite import FavoriteCreate
from typing import List, Optional, Dict


CONTENT_MODELS = {
	"movie": Movie,
	"show": Show,
	"breaking_news": BreakingNews,
	"divertissement": Divertissement,
	"reel": Reel,
	"reportage": Reportage,
	"jtandmag": JTandMag,
	"popular_program": PopularPrograms,
	"sport": Sport,
	"emission_category": EmissionCategory,
	"series": Series
}


async def _get_content(content_type: str, content_id: str):
	model = CONTENT_MODELS.get(content_type)
	if not model:
		return None
	return await model.get(content_id)

async def add_favorite(user_id: str, data: FavoriteCreate) -> Optional[Dict]:
	"""Toggle favori (ajouter ou retirer) - évite les doublons"""
	# Vérifier que le contenu existe
	content = await _get_content(data.content_type, data.content_id)
	if not content:
		return None
	
	# Vérifier si déjà en favoris
	existing = await Favorite.find_one(
		Favorite.user_id == user_id,
		Favorite.content_id == data.content_id,
		Favorite.content_type == data.content_type
	)
	
	if existing:
		# Retirer le favori existant (toggle off)
		print(f"💔 Retrait du favori existant: {existing.id}")
		await existing.delete()
		return {
			"success": True,
			"action": "removed",
			"message": "Retiré des favoris"
		}
	
	# Ajouter le favori (toggle on)
	print(f"⭐ Ajout d'un nouveau favori")
	fav = Favorite(
		user_id=user_id,
		content_id=data.content_id,
		content_type=data.content_type
	)
	await fav.insert()
	
	# Envoyer une notification
	try:
		from app.services.notification_service import send_favorite_added_notification
		content_title = content.title if hasattr(content, 'title') else "Contenu"
		await send_favorite_added_notification(user_id, content_title, data.content_type)
	except Exception as e:
		print(f"⚠️ Erreur envoi notification favori: {e}")
	
	return {
		"success": True,
		"action": "added",
		"message": "Ajouté aux favoris",
		"favorite_id": str(fav.id),
		"content_type": data.content_type
	}

async def get_favorite(fav_id: str) -> Optional[Favorite]:
	return await Favorite.get(fav_id)

async def list_favorites(user_id: str, content_type: str = None) -> List[Dict]:
	"""Lister les favoris avec enrichissement du contenu"""
	print(f"🔍 [Backend] list_favorites appelé - user_id: {user_id}, content_type: {content_type}")
	
	query = Favorite.find(Favorite.user_id == user_id)
	
	# Ajouter le filtrage par type de contenu
	if content_type:
		print(f"🔍 [Backend] Application du filtre: content_type={content_type}")
		query = query.find(Favorite.content_type == content_type)
	else:
		print(f"📋 [Backend] Aucun filtre appliqué")
	
	favorites = await query.to_list()
	print(f"📊 [Backend] Nombre de favoris trouvés: {len(favorites)}")
	
	if content_type:
		print(f"✅ [Backend] Filtrage {content_type} appliqué avec succès")
	else:
		print(f"📋 [Backend] Tous les favoris retournés")
	
	enriched_favorites = []
	for fav in favorites:
		fav_dict = fav.dict()

		content = await _get_content(fav.content_type, fav.content_id)
		if content:
			fav_dict['content_title'] = getattr(content, 'title', None) or getattr(content, 'name', None)
			fav_dict['content_type'] = fav.content_type
			fav_dict['image_url'] = (
				getattr(content, 'image_url', None) or 
				getattr(content, 'image', None) or 
				getattr(content, 'image_main', None) or 
				getattr(content, 'thumbnail', None)
			)
		
		enriched_favorites.append(fav_dict)
	
	return enriched_favorites

async def remove_favorite(fav_id: str, user_id: str) -> bool:
	"""Supprimer un favori (seulement par le propriétaire)"""
	fav = await Favorite.get(fav_id)
	if not fav or fav.user_id != user_id:
		return False
	await fav.delete()
	return True

async def remove_favorite_by_content(user_id: str, content_id: str, content_type: str) -> bool:
	"""Supprimer un favori par contenu"""
	fav = await Favorite.find_one(
		Favorite.user_id == user_id,
		Favorite.content_id == content_id,
		Favorite.content_type == content_type
	)
	
	if not fav:
		return False
	
	await fav.delete()
	return True

async def get_all_favorites(skip: int = 0, limit: int = 1000) -> List[Dict]:
	"""Récupérer tous les favoris (pour admin)"""
	favorites = await Favorite.find().skip(skip).limit(limit).to_list()
	return [fav.dict() for fav in favorites]
