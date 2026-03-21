from app.models.reel import Reel
from app.schemas.reel import ReelCreate, ReelUpdate
from typing import List, Optional
from datetime import datetime, timedelta
import math


async def create_reel(data: ReelCreate) -> Reel:
	reel = Reel(**data.dict())
	await reel.insert()
	return reel


def calculate_reel_score(reel: dict) -> float:
	"""
	Calcule un score de recommandation pour un reel basé sur :
	- L'engagement (likes, comments, shares, views)
	- La récence (temps de publication)
	
	Algorithme inspiré de TikTok/Facebook :
	- Engagement Rate : pondération des interactions par rapport aux vues
	- Time Decay : pénalité pour les contenus anciens
	- Viral Boost : bonus pour les contenus qui performent rapidement
	"""
	
	# Récupérer les métriques
	likes = reel.get('likes', 0)
	comments = reel.get('comments', 0)
	shares = reel.get('shares', 0)
	views = max(reel.get('views', 1), 1)  # Éviter division par zéro
	created_at = reel.get('created_at')
	
	# 1. ENGAGEMENT SCORE (0-1000 points)
	# Pondération : shares > comments > likes (actions plus engageantes)
	engagement_points = (
		likes * 1 +           # 1 point par like
		comments * 5 +        # 5 points par commentaire
		shares * 10           # 10 points par partage
	)
	
	# Taux d'engagement (engagement / vues)
	engagement_rate = engagement_points / views
	
	# Normaliser l'engagement score (avec logarithme pour éviter les valeurs trop élevées)
	engagement_score = math.log(1 + engagement_rate * 100) * 100
	
	# 2. TIME DECAY FACTOR (0-1)
	# Plus le contenu est récent, plus il a de chances d'apparaître
	now = datetime.utcnow()
	age_hours = (now - created_at).total_seconds() / 3600
	
	# Décroissance exponentielle : 
	# - Contenu < 6h : 100% du score
	# - Contenu 24h : ~60% du score
	# - Contenu 48h : ~40% du score
	# - Contenu 7j : ~10% du score
	half_life_hours = 24  # Demi-vie de 24h
	time_decay = math.exp(-age_hours / (half_life_hours * 1.44))
	
	# 3. VIRAL BOOST (1-3x multiplier)
	# Si un contenu a beaucoup d'engagement rapidement, on le pousse plus
	engagement_velocity = engagement_points / max(age_hours, 1)
	
	if engagement_velocity > 50:  # Très viral
		viral_boost = 3.0
	elif engagement_velocity > 20:  # Viral
		viral_boost = 2.0
	elif engagement_velocity > 5:  # Bon engagement
		viral_boost = 1.5
	else:
		viral_boost = 1.0
	
	# 4. VIEW COMPLETION BONUS
	# Si beaucoup de vues mais peu d'engagement, c'est peut-être du clickbait
	# On donne un léger bonus si l'engagement est bon relatif aux vues
	if views > 100 and engagement_rate > 0.1:  # 10% d'engagement
		completion_bonus = 1.2
	else:
		completion_bonus = 1.0
	
	# SCORE FINAL
	final_score = engagement_score * time_decay * viral_boost * completion_bonus
	
	return final_score


async def list_reels(skip: int = 0, limit: int = 50) -> List[Reel]:
	try:
		# Récupérer TOUS les reels (on va les trier après)
		# On en prend plus que demandé pour avoir un bon pool à trier
		fetch_limit = max(limit * 3, 150)  # 3x le limit pour avoir du choix
		
		reels = await Reel.find_all().sort(-Reel.created_at).limit(fetch_limit).to_list()
		
		# Convertir en dict et calculer le score
		scored_reels = []
		for reel in reels:
			reel_dict = reel.dict()
			reel_dict['id'] = str(reel.id)
			reel_dict['video_url'] = str(reel.video_url) if reel.video_url else None
			reel_dict['videoUrl'] = str(reel.video_url) if reel.video_url else None
			
			# Calculer le score de recommandation
			score = calculate_reel_score(reel_dict)
			reel_dict['_score'] = score  # Garder le score pour debug (optionnel)
			
			scored_reels.append((score, reel_dict))
		
		# Trier par score décroissant
		scored_reels.sort(key=lambda x: x[0], reverse=True)
		
		# Appliquer la pagination sur les résultats triés
		paginated_reels = scored_reels[skip:skip + limit]
		
		# Retourner seulement les dicts (sans le score)
		result = [reel for score, reel in paginated_reels]
		
		return result
	except Exception as e:
		print(f"❌ Erreur list_reels: {str(e)}")
		return []


async def update_reel(reel_id: str, data: ReelUpdate) -> Optional[Reel]:
	reel = await Reel.get(reel_id)
	if not reel:
		return None

	update_data = data.dict(exclude_unset=True)
	for field, value in update_data.items():
		setattr(reel, field, value)

	reel.updated_at = datetime.utcnow()
	await reel.save()
	return reel


async def delete_reel(reel_id: str) -> bool:
	reel = await Reel.get(reel_id)
	if not reel:
		return False
	await reel.delete()
	return True


async def increment_reel_view(reel_id: str) -> bool:
	"""Incrémenter le compteur de vues d'un reel"""
	try:
		reel = await Reel.get(reel_id)
		if not reel:
			return False
		
		reel.views = (reel.views or 0) + 1
		await reel.save()
		return True
	except Exception as e:
		print(f"❌ Erreur increment_reel_view: {str(e)}")
		return False


async def get_reel(reel_id: str) -> Optional[Reel]:
	return await Reel.get(reel_id)
