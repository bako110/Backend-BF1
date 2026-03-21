from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate
from typing import List, Optional
from datetime import datetime
from app.utils.subscription_utils import can_access_content, get_highest_active_category

async def get_all_subscriptions(skip: int = 0, limit: int = 1000) -> List:
    """Récupérer tous les abonnements (pour admin)"""
    subscriptions = await Subscription.find().skip(skip).limit(limit).to_list()
    return [sub.dict() for sub in subscriptions]

async def create_subscription(data: SubscriptionCreate) -> Subscription:
	"""
	Crée un nouvel abonnement et met à jour le statut premium de l'utilisateur.
	Si un plan_id est fourni, calcule automatiquement la end_date.
	"""
	from app.models.user import User
	from dateutil.relativedelta import relativedelta
	
	now = datetime.utcnow()
	
	# Créer l'abonnement
	sub_data = data.dict()
	
	print(f"🔍 [DEBUG] Données reçues pour création abonnement:")
	print(f"  - user_id: {sub_data.get('user_id')}")
	print(f"  - plan_id: {sub_data.get('plan_id')}")
	print(f"  - category (frontend): {sub_data.get('category')}")
	
	# Si pas de start_date, utiliser maintenant
	if not sub_data.get('start_date'):
		sub_data['start_date'] = now
	
	# Si on a un plan_id, récupérer les infos du plan
	plan = None
	if 'plan_id' in sub_data and sub_data['plan_id']:
		from app.models.subscription_plan import SubscriptionPlan
		
		plan_id = sub_data['plan_id']
		print(f"🔍 Recherche du plan avec ID: {plan_id}")
		
		plan = await SubscriptionPlan.get(plan_id)
		
		if plan:
			print(f"✅ Plan trouvé: {plan.name} (code: {plan.code}, category: {plan.category})")
			# Toujours récupérer la catégorie du plan
			sub_data['category'] = plan.category
			print(f"✅ Catégorie assignée à l'abonnement: {plan.category}")
			
			# Calculer end_date si nécessaire
			if not sub_data.get('end_date'):
				start = sub_data['start_date']
				sub_data['end_date'] = start + relativedelta(months=plan.duration_months)
				print(f"✅ end_date calculée: {sub_data['end_date']} (durée: {plan.duration_months} mois)")
		else:
			print(f"❌ ERREUR: Plan {plan_id} introuvable dans la base de données!")
			print(f"   Type de plan_id: {type(plan_id)}")
	else:
		print(f"⚠️ Aucun plan_id fourni dans les données")
	
	print(f"📝 Catégorie finale avant insertion: {sub_data.get('category')}")
	
	sub = Subscription(**sub_data)
	await sub.insert()
	
	print(f"✅ Abonnement créé avec ID: {sub.id}, category: {sub.category}")
	
	# Mettre à jour le statut premium et la catégorie de l'utilisateur
	await sync_user_premium_status(data.user_id)
		
	# Envoyer une notification premium
	try:
		from app.services.notification_service import send_premium_notification
		await send_premium_notification(data.user_id)
	except Exception as e:
		print(f"⚠️ Erreur envoi notification premium: {e}")
	
	return sub

async def get_subscription(sub_id: str) -> Optional[Subscription]:
	return await Subscription.get(sub_id)

async def list_subscriptions(user_id: str) -> List[Subscription]:
	return await Subscription.find(Subscription.user_id == user_id).to_list()

async def cancel_subscription(sub_id: str) -> bool:
	sub = await Subscription.get(sub_id)
	if not sub:
		return False
	sub.is_active = False
	await sub.save()
	
	# Mettre à jour le statut premium de l'utilisateur
	from app.models.user import User
	user = await User.get(sub.user_id)
	if user:
		# Vérifier s'il a encore un autre abonnement actif
		has_active_sub = await check_user_has_active_subscription(sub.user_id)
		user.is_premium = has_active_sub
		await user.save()
	
	return True

async def check_user_has_active_subscription(user_id: str) -> bool:
	"""
	Vérifie si un utilisateur a au moins un abonnement actif et non expiré.
	Retourne True si l'utilisateur a un abonnement valide, False sinon.
	"""
	now = datetime.utcnow()
	
	# Chercher un abonnement actif qui n'est pas expiré
	active_sub = await Subscription.find_one({
		"user_id": user_id,
		"is_active": True,
		"$or": [
			{"end_date": None},  # Abonnement sans date de fin (à vie)
			{"end_date": {"$gt": now}}  # Date de fin dans le futur
		]
	})
	
	return active_sub is not None

async def get_user_subscription_category(user_id: str) -> Optional[str]:
	"""
	Récupère la catégorie d'abonnement active de l'utilisateur.
	Si l'utilisateur a plusieurs abonnements actifs, retourne la catégorie la plus élevée.
	
	Args:
		user_id: ID de l'utilisateur
		
	Returns:
		'basic', 'standard', 'premium' ou None si pas d'abonnement actif
	"""
	now = datetime.utcnow()
	
	# Récupérer tous les abonnements actifs de l'utilisateur
	active_subs = await Subscription.find({
		"user_id": user_id,
		"is_active": True,
		"$or": [
			{"end_date": None},
			{"end_date": {"$gt": now}}
		]
	}).to_list()
	
	if not active_subs:
		return None
	
	# Si l'utilisateur a plusieurs abonnements, prendre la catégorie la plus élevée
	categories = [sub.category for sub in active_subs if sub.category]
	return get_highest_active_category(categories)

async def sync_user_premium_status(user_id: str) -> bool:
	"""
	Synchronise le statut is_premium et subscription_category d'un utilisateur 
	en fonction de ses abonnements actifs.
	Retourne le nouveau statut premium.
	"""
	from app.models.user import User
	
	has_active_sub = await check_user_has_active_subscription(user_id)
	category = await get_user_subscription_category(user_id)
	
	user = await User.get(user_id)
	if user:
		changed = False
		
		if user.is_premium != has_active_sub:
			user.is_premium = has_active_sub
			changed = True
			
		if user.subscription_category != category:
			user.subscription_category = category
			changed = True
		
		if changed:
			await user.save()
			print(f"✅ Statut synchronisé pour user {user_id}: premium={has_active_sub}, category={category}")
	
	return has_active_sub

async def deactivate_expired_subscriptions() -> int:
	"""
	Désactive tous les abonnements expirés et met à jour le statut premium des utilisateurs.
	Retourne le nombre d'abonnements désactivés.
	"""
	now = datetime.utcnow()
	
	# Trouver tous les abonnements actifs avec une date de fin passée
	expired_subs = await Subscription.find({
		"is_active": True,
		"end_date": {"$lt": now, "$ne": None}
	}).to_list()
	
	count = 0
	affected_users = set()
	
	for sub in expired_subs:
		sub.is_active = False
		await sub.save()
		affected_users.add(sub.user_id)
		count += 1
	
	# Mettre à jour le statut premium de tous les utilisateurs affectés
	for user_id in affected_users:
		await sync_user_premium_status(user_id)
	
	if count > 0:
		print(f"✅ {count} abonnements expirés désactivés, {len(affected_users)} utilisateurs mis à jour")
	
	return count
