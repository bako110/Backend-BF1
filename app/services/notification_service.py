
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.models.user import User
from typing import List, Optional

async def delete_notification(notif_id: str, user_id: str) -> bool:
	try:
		print(f"🗑️ [NotificationService] Tentative suppression notification {notif_id} pour user {user_id}")
		notif = await Notification.get(notif_id)
		if not notif:
			print(f"❌ [NotificationService] Notification {notif_id} non trouvée")
			return False
		if notif.user_id != user_id:
			print(f"❌ [NotificationService] User {user_id} non autorisé (owner: {notif.user_id})")
			return False
		await notif.delete()
		print(f"✅ [NotificationService] Notification {notif_id} supprimée")
		return True
	except Exception as e:
		print(f"❌ [NotificationService] Erreur suppression: {e}")
		return False

async def create_notification(data: NotificationCreate) -> Notification:
	notif = Notification(**data.dict())
	await notif.insert()
	return notif

async def get_notification(notif_id: str) -> Optional[Notification]:
	return await Notification.get(notif_id)

async def list_notifications(user_id: str, unread_only: bool = False) -> List[Notification]:
	if unread_only:
		return await Notification.find(Notification.user_id == user_id, Notification.is_read == False).to_list()
	return await Notification.find(Notification.user_id == user_id).to_list()

async def mark_as_read(notif_id: str) -> bool:
	notif = await Notification.get(notif_id)
	if not notif:
		return False
	notif.is_read = True
	await notif.save()
	return True

async def mark_all_as_read(user_id: str) -> int:
	"""Marquer toutes les notifications d'un utilisateur comme lues"""
	try:
		notifications = await Notification.find(Notification.user_id == user_id, Notification.is_read == False).to_list()
		count = 0
		for notif in notifications:
			notif.is_read = True
			await notif.save()
			count += 1
		print(f"✅ [NotificationService] {count} notifications marquées comme lues pour user {user_id}")
		return count
	except Exception as e:
		print(f"❌ [NotificationService] Erreur mark_all_as_read: {e}")
		return 0

async def delete_all_notifications(user_id: str) -> int:
	"""Supprimer toutes les notifications d'un utilisateur"""
	try:
		notifications = await Notification.find(Notification.user_id == user_id).to_list()
		count = 0
		for notif in notifications:
			await notif.delete()
			count += 1
		print(f"✅ [NotificationService] {count} notifications supprimées pour user {user_id}")
		return count
	except Exception as e:
		print(f"❌ [NotificationService] Erreur delete_all_notifications: {e}")
		return 0

# ============ NOTIFICATIONS AUTOMATIQUES ============

async def send_welcome_notification(user_id: str, username: str):
	"""Envoyer une notification de bienvenue à un nouvel utilisateur"""
	try:
		notification = Notification(
			user_id=user_id,
			title="Bienvenue sur BF1 TV! 🎉",
			message=f"Bonjour {username}! Bienvenue sur BF1 TV. Profitez de nos films, émissions et actualités en direct.",
			category="welcome",
			is_read=False
		)
		await notification.insert()
		print(f"✅ Notification de bienvenue envoyée à {username}")
		return notification
	except Exception as e:
		print(f"❌ Erreur envoi notification bienvenue: {e}")
		return None

async def send_favorite_added_notification(user_id: str, content_title: str, content_type: str):
	"""Envoyer une notification quand un contenu est ajouté aux favoris"""
	try:
		type_map = {
			"movie": "film",
			"show": "émission",
			"breaking_news": "actualité",
			"interview": "interview",
			"reel": "reel",
			"replay": "replay",
			"trending_show": "tendance",
			"popular_program": "programme"
		}
		type_text = type_map.get(content_type, "contenu")
		notification = Notification(
			user_id=user_id,
			title="Ajouté aux favoris ⭐",
			message=f"'{content_title}' a été ajouté à vos favoris. Retrouvez tous vos {type_text}s favoris dans votre profil.",
			category="favorite",
			is_read=False
		)
		await notification.insert()
		print(f"✅ Notification favori envoyée pour {content_title}")
		return notification
	except Exception as e:
		print(f"❌ Erreur envoi notification favori: {e}")
		return None

async def notify_all_users_new_movie(movie_title: str, movie_id: str):
	"""Notifier tous les utilisateurs d'un nouveau film"""
	try:
		users = await User.find_all().to_list()
		count = 0
		for user in users:
			notification = Notification(
				user_id=str(user.id),
				title="Nouveau film disponible 🎬",
				message=f"Le film '{movie_title}' est maintenant disponible sur BF1 TV. Ne le manquez pas!",
				category="new_movie",
				is_read=False
			)
			await notification.insert()
			count += 1
		print(f"✅ {count} notifications envoyées pour le nouveau film '{movie_title}'")
		return count
	except Exception as e:
		print(f"❌ Erreur envoi notifications nouveau film: {e}")
		return 0

async def notify_all_users_new_news(news_title: str, news_id: str):
	"""Notifier tous les utilisateurs d'une nouvelle actualité"""
	try:
		users = await User.find_all().to_list()
		count = 0
		for user in users:
			notification = Notification(
				user_id=str(user.id),
				title="Nouvelle actualité 📰",
				message=f"Nouvelle actualité: {news_title}. Consultez-la dès maintenant!",
				category="new_news",
				is_read=False
			)
			await notification.insert()
			count += 1
		print(f"✅ {count} notifications envoyées pour la nouvelle actualité '{news_title}'")
		return count
	except Exception as e:
		print(f"❌ Erreur envoi notifications nouvelle actualité: {e}")
		return 0

async def notify_all_users_new_show(show_title: str, show_id: str):
	"""Notifier tous les utilisateurs d'une nouvelle émission"""
	try:
		users = await User.find_all().to_list()
		count = 0
		for user in users:
			notification = Notification(
				user_id=str(user.id),
				title="Nouvelle émission 📺",
				message=f"L'émission '{show_title}' est maintenant disponible sur BF1 TV!",
				category="new_show",
				is_read=False
			)
			await notification.insert()
			count += 1
		print(f"✅ {count} notifications envoyées pour la nouvelle émission '{show_title}'")
		return count
	except Exception as e:
		print(f"❌ Erreur envoi notifications nouvelle émission: {e}")
		return 0

async def send_premium_notification(user_id: str):
	"""Notifier un utilisateur qu'il est devenu premium"""
	try:
		notification = Notification(
			user_id=user_id,
			title="Vous êtes maintenant Premium! 🌟",
			message="Félicitations! Vous avez accès à tous les contenus premium de BF1 TV.",
			category="premium",
			is_read=False
		)
		await notification.insert()
		print(f"✅ Notification premium envoyée")
		return notification
	except Exception as e:
		print(f"❌ Erreur envoi notification premium: {e}")
		return None
