from typing import List, Optional
from datetime import datetime
import asyncio
import aiohttp
import json

# ─── Firebase Admin SDK ───────────────────────────────────────────────────────
try:
    import firebase_admin
    from firebase_admin import credentials, messaging as fcm_messaging
    _firebase_available = True
except ImportError:
    _firebase_available = False

def _init_firebase():
    """Initialise Firebase Admin SDK si pas encore fait."""
    if not _firebase_available:
        return False
    if firebase_admin._apps:
        return True
    import os, json, base64, tempfile

    # ── Credentials hardcodes ─────────────────────────────────────────────────
    service_account_info = {
        "type": "service_account",
        "project_id": "bf1-tv-afb6a",
        "private_key_id": "REDACTED",
        "private_key": "REDACTED",
        "client_email": "REDACTED",
        "client_id": "REDACTED",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "REDACTED",
        "universe_domain": "googleapis.com"
    }
    try:
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        print("[OK] Firebase Admin SDK initialise")
        return True
    except Exception as e:
        print(f"[ERREUR] Initialisation Firebase: {e}")
        return False

# Tenter l'initialisation au démarrage
_firebase_ready = _init_firebase()


class PushNotificationService:
    def __init__(self):
        # Configuration pour le service de notifications push
        self.fcm_server_key = None  # Clé FCM pour Firebase (si utilisé)
        # Plus besoin de mobile_app_url - on utilise WebSocket pour tout le monde

    async def send_welcome_notification(self, user_id: str, username: str):
        """Envoyer une notification de bienvenue (déjà géré côté mobile)"""
        try:
            print(f"✅ Notification de bienvenue envoyée à {username}")
            return True
        except Exception as e:
            print(f"❌ Erreur notification bienvenue: {e}")
            return False

    async def send_popular_program_notification(self, program_data: dict):
        """Envoyer une notification pour un nouveau programme populaire"""
        try:
            notification = {
                "title": "🌟 Nouveau Programme Populaire",
                "body": f"{program_data.get('title', 'Nouveau programme')} est maintenant disponible !",
                "data": {
                    "type": "popular_program",
                    "program_id": str(program_data.get('_id', program_data.get('id'))),
                    "title": program_data.get('title', ''),
                    "description": program_data.get('description', '')
                }
            }

            success = await self._broadcast_notification(notification)
            if success:
                print(f"✅ Notification programme populaire envoyée: {program_data.get('title')}")

            return success
        except Exception as e:
            print(f"❌ Erreur notification programme populaire: {e}")
            return False

    async def send_flash_info_notification(self, flash_info_data: dict):
        """Envoyer une notification pour un flash info"""
        try:
            print(f"📱 Préparation notification flash info...")
            print(f"📱 Données reçues: {flash_info_data}")

            notification = {
                "title": "⚡ FLASH INFO",
                "body": flash_info_data.get('title', flash_info_data.get('description', 'Dernière minute : une information importante vient d\'arriver')),
                "data": {
                    "type": "flash_info",
                    "flash_info_id": flash_info_data.get('_id', flash_info_data.get('id')),
                    "title": flash_info_data.get('title', ''),
                    "description": flash_info_data.get('description', '')
                }
            }

            print(f"📱 Notification créée: {notification['title']}")
            print(f"📱 Corps: {notification['body']}")

            success = await self._broadcast_notification(notification)
            if success:
                print(f"✅ Notification flash info envoyée avec succès")

            return success
        except Exception as e:
            print(f"❌ Erreur notification flash info: {e}")
            print(f"❌ Détails erreur: {str(e)}")
            return False

    async def _broadcast_notification(self, notification: dict) -> bool:
        """Diffuser une notification à tous les utilisateurs (WebSocket + FCM Firebase)"""
        try:
            # ── 1. WebSocket (onglets ouverts) ────────────────────────────────
            from app.services.websocket_service import websocket_manager

            print(f"📱 Notification à diffuser: {notification['title']}")
            print(f"📱 Contenu: {notification['body']}")
            print(f"📱 Données: {notification['data']}")

            await websocket_manager.send_notification(
                notification_type=notification['data']['type'],
                data=notification
            )

            # ── 2. FCM Firebase (onglets fermés / mobile) ─────────────────────
            await self._send_fcm_to_all(notification)

            return True

        except Exception as e:
            print(f"❌ Erreur diffusion notification: {e}")
            return False

    async def _send_fcm_to_all(self, notification: dict):
        """Envoyer la notification FCM à tous les tokens enregistrés en base."""
        if not _firebase_available or not firebase_admin._apps:
            return

        try:
            from app.models.user import User
            # Récupérer tous les tokens FCM non-vides
            users = await User.find({"fcm_tokens": {"$exists": True, "$not": {"$size": 0}}}).to_list()
            tokens = [t for u in users if u.fcm_tokens for t in u.fcm_tokens if t]

            if not tokens:
                print("📱 FCM: aucun token enregistré.")
                return

            data_payload = {k: str(v) for k, v in notification.get('data', {}).items()}

            # Envoi par lots de 500 (limite FCM)
            batch_size = 500
            for i in range(0, len(tokens), batch_size):
                batch = tokens[i:i + batch_size]
                message = fcm_messaging.MulticastMessage(
                    notification=fcm_messaging.Notification(
                        title=notification['title'],
                        body=notification['body'],
                    ),
                    data=data_payload,
                    tokens=batch,
                    webpush=fcm_messaging.WebpushConfig(
                        notification=fcm_messaging.WebpushNotification(
                            icon='/assets/images/logo.png',
                        )
                    ),
                )
                response = fcm_messaging.send_each_for_multicast(message)
                print(f"✅ FCM: {response.success_count}/{len(batch)} envoyés, {response.failure_count} échoués")

                # Nettoyer les tokens invalides
                await self._cleanup_invalid_tokens(batch, response)

        except Exception as e:
            print(f"❌ Erreur envoi FCM: {e}")

    async def _cleanup_invalid_tokens(self, tokens: list, response):
        """Supprimer les tokens FCM invalides de la base."""
        try:
            from app.models.user import User
            invalid_tokens = [
                tokens[idx]
                for idx, res in enumerate(response.responses)
                if not res.success and res.exception and 'registration-token-not-registered' in str(res.exception)
            ]
            if not invalid_tokens:
                return
            users = await User.find({"fcm_tokens": {"$in": invalid_tokens}}).to_list()
            for user in users:
                user.fcm_tokens = [t for t in user.fcm_tokens if t not in invalid_tokens]
                await user.save()
            print(f"🧹 FCM: {len(invalid_tokens)} token(s) invalide(s) supprimé(s)")
        except Exception as e:
            print(f"❌ Erreur nettoyage tokens FCM: {e}")

    async def send_daily_news_notification(self, journal_type: str):
        """Envoyer les notifications quotidiennes pour les journaux"""
        try:
            if journal_type == "13h30":
                notification = {
                    "title": "📰 Journal 13H30 disponible !",
                    "body": "Ne manquez pas le journal de 13H30 avec toute l'actualité de la journée !",
                    "data": {
                        "type": "daily_news",
                        "journal_type": "13h30"
                    }
                }
            elif journal_type == "19h30":
                notification = {
                    "title": "📺 Journal 19H30 est en direct !",
                    "body": "Le journal de 19H30 est en direct ! Toute l'actualité à ne pas manquer.",
                    "data": {
                        "type": "daily_news",
                        "journal_type": "19h30"
                    }
                }
            else:
                return False

            success = await self._broadcast_notification(notification)
            if success:
                print(f"✅ Notification journal {journal_type} envoyée")

            return success
        except Exception as e:
            print(f"❌ Erreur notification journal {journal_type}: {e}")
            return False

# Instance globale du service
push_notification_service = PushNotificationService()
