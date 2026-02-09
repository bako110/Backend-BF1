from typing import List, Optional
from datetime import datetime
import asyncio
import aiohttp
import json

class PushNotificationService:
    def __init__(self, mobile_app_url=None):
        # Configuration pour le service de notifications push
        self.fcm_server_key = None  # Clé FCM pour Firebase (si utilisé)
        self.mobile_app_url = mobile_app_url or "http://10.10.0.8:3000"  # URL de l'app mobile pour les tests
        
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
            # Créer le message de notification
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
            
            # Envoyer à tous les utilisateurs connectés
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
            
            # Créer le message de notification urgent
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
            
            # Envoyer à tous les utilisateurs connectés
            success = await self._broadcast_notification(notification)
            if success:
                print(f"✅ Notification flash info envoyée avec succès")
            
            return success
        except Exception as e:
            print(f"❌ Erreur notification flash info: {e}")
            print(f"❌ Détails erreur: {str(e)}")
            return False
    
    async def _broadcast_notification(self, notification: dict) -> bool:
        """Diffuser une notification à tous les utilisateurs mobiles"""
        try:
            # Utiliser WebSocket pour les notifications en temps réel
            from app.services.websocket_service import websocket_manager
            
            print(f"📱 Notification à diffuser: {notification['title']}")
            print(f"📱 Contenu: {notification['body']}")
            print(f"📱 Données: {notification['data']}")
            
            # Envoyer via WebSocket aux clients connectés
            await websocket_manager.send_notification(
                notification_type=notification['data']['type'],
                data=notification
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur diffusion notification: {e}")
            return False
    
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
