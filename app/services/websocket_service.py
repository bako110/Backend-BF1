from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Optional
import json
import asyncio
import uuid
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        # Liste des connexions WebSocket actives
        self.active_connections: List[WebSocket] = []
        # Dictionnaire pour stocker les informations sur les connexions
        self.connection_info: Dict[WebSocket, dict] = {}
        # Tracking des utilisateurs regardant le livestream
        self.livestream_viewers: set = set()
        self.livestream_connections: List[WebSocket] = []

        # ── Chat live ────────────────────────────────────────────────────────
        # Historique des messages en mémoire (max 200)
        self.chat_messages: List[dict] = []
        self.MAX_CHAT_MESSAGES = 200
        # IDs des messages masqués/supprimés par l'admin
        self.hidden_message_ids: set = set()
        # Statut du chat (ouvert / fermé par l'admin)
        self.chat_open: bool = True
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accepter une nouvelle connexion WebSocket"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = {
            "client_id": client_id or f"client_{len(self.active_connections)}",
            "connected_at": asyncio.get_event_loop().time()
        }
        print(f"🔌 Client connecté: {self.connection_info[websocket]['client_id']}")
        print(f"📊 Total connexions: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Déconnecter un client WebSocket"""
        if websocket in self.active_connections:
            client_id = self.connection_info.get(websocket, {}).get("client_id", "unknown")
            user_id = self.connection_info.get(websocket, {}).get("user_id")
            
            # Retirer du livestream si l'utilisateur regardait
            if websocket in self.livestream_connections:
                self.livestream_connections.remove(websocket)
                if user_id and user_id in self.livestream_viewers:
                    self.livestream_viewers.remove(user_id)
                print(f"🎥 Spectateur retiré du livestream: {client_id}")
            
            self.active_connections.remove(websocket)
            if websocket in self.connection_info:
                del self.connection_info[websocket]
            print(f"🔌 Client déconnecté: {client_id}")
            print(f"📊 Total connexions: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Envoyer un message à un client spécifique"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ Erreur envoi message personnel: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Diffuser un message à tous les clients connectés"""
        if not self.active_connections:
            print("📱 Aucun client connecté pour recevoir la notification")
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"❌ Erreur envoi à client: {e}")
                disconnected.append(connection)
        
        # Nettoyer les connexions déconnectées
        for connection in disconnected:
            self.disconnect(connection)
        
        print(f"📱 Notification diffusée à {len(self.active_connections) - len(disconnected)} clients")
    
    async def send_notification(self, notification_type: str, data: dict):
        """Envoyer une notification push via WebSocket"""
        message = {
            "type": "push_notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.broadcast(message)
    
    async def get_connection_count(self) -> int:
        """Obtenir le nombre de clients connectés"""
        return len(self.active_connections)
    
    async def join_livestream(self, websocket: WebSocket, user_id: str = None):
        """Ajouter un utilisateur aux spectateurs du livestream"""
        if websocket not in self.livestream_connections:
            self.livestream_connections.append(websocket)
            
        if user_id:
            self.livestream_viewers.add(user_id)
            self.connection_info[websocket]['watching_live'] = True
            self.connection_info[websocket]['user_id'] = user_id
            print(f"🎥 Utilisateur {user_id} rejoint le livestream")
        else:
            # Visiteur anonyme
            client_id = self.connection_info.get(websocket, {}).get('client_id', 'anonymous')
            self.connection_info[websocket]['watching_live'] = True
            print(f"🎥 Visiteur anonyme {client_id} rejoint le livestream")
            
        print(f"📊 Spectateurs livestream: {self.get_livestream_viewer_count()}")
        
        # Notifier les autres spectateurs du changement
        await self.broadcast_to_livestream({'type': 'viewer_joined', 'total_viewers': self.get_livestream_viewer_count()})
    
    async def leave_livestream(self, websocket: WebSocket, user_id: str = None):
        """Retirer un utilisateur des spectateurs du livestream"""
        if websocket in self.livestream_connections:
            self.livestream_connections.remove(websocket)
            
        if user_id and user_id in self.livestream_viewers:
            self.livestream_viewers.remove(user_id)
            print(f"🎥 Utilisateur {user_id} quitte le livestream")
        else:
            client_id = self.connection_info.get(websocket, {}).get('client_id', 'anonymous')
            print(f"🎥 Visiteur anonyme {client_id} quitte le livestream")
            
        if websocket in self.connection_info:
            self.connection_info[websocket]['watching_live'] = False
            
        print(f"📊 Spectateurs livestream: {self.get_livestream_viewer_count()}")
        
        # Notifier les autres spectateurs du changement
        await self.broadcast_to_livestream({'type': 'viewer_left', 'total_viewers': self.get_livestream_viewer_count()})
    
    def get_livestream_viewer_count(self) -> int:
        """Obtenir le nombre réel de spectateurs du livestream"""
        # Compter les connexions actives qui regardent le live
        active_livestream_viewers = 0
        for websocket in self.livestream_connections:
            if websocket in self.active_connections:  # Vérifier que la connexion est toujours active
                active_livestream_viewers += 1
        return active_livestream_viewers
    
    async def broadcast_to_livestream(self, message: dict):
        """Diffuser un message uniquement aux spectateurs du livestream"""
        if not self.livestream_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.livestream_connections:
            if connection in self.active_connections:  # Vérifier que la connexion est active
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    print(f"❌ Erreur envoi à spectateur livestream: {e}")
                    disconnected.append(connection)
        
        # Nettoyer les connexions déconnectées
        for connection in disconnected:
            if connection in self.livestream_connections:
                self.livestream_connections.remove(connection)
                user_id = self.connection_info.get(connection, {}).get('user_id')
                if user_id and user_id in self.livestream_viewers:
                    self.livestream_viewers.remove(user_id)
        
        print(f"🎥 Message diffusé à {len(self.livestream_connections) - len(disconnected)} spectateurs livestream")

    # ── Méthodes Chat Live ────────────────────────────────────────────────────

    def _visible_messages(self) -> List[dict]:
        """Retourne les messages non masqués (pour broadcast)"""
        return [m for m in self.chat_messages if m['id'] not in self.hidden_message_ids]

    async def add_chat_message(self, user_id: Optional[str], username: str,
                               avatar_url: Optional[str], text: str) -> Optional[dict]:
        """Ajouter un message chat et broadcaster à tous les spectateurs du live.
        Retourne None si le chat est fermé."""
        if not self.chat_open:
            return None

        msg = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": username,
            "avatar_url": avatar_url,
            "text": text,
            "created_at": datetime.utcnow().isoformat(),
        }

        self.chat_messages.append(msg)
        # Garder seulement les MAX_CHAT_MESSAGES derniers
        if len(self.chat_messages) > self.MAX_CHAT_MESSAGES:
            self.chat_messages = self.chat_messages[-self.MAX_CHAT_MESSAGES:]

        await self.broadcast_to_livestream({
            "type": "chat_message",
            "message": msg
        })
        return msg

    async def hide_chat_message(self, message_id: str) -> bool:
        """Masquer un message (admin). Broadcaster l'événement."""
        self.hidden_message_ids.add(message_id)
        await self.broadcast_to_livestream({
            "type": "chat_message_hidden",
            "message_id": message_id
        })
        return True

    async def delete_chat_message(self, message_id: str) -> bool:
        """Supprimer définitivement un message (admin). Broadcaster l'événement."""
        self.chat_messages = [m for m in self.chat_messages if m['id'] != message_id]
        self.hidden_message_ids.discard(message_id)
        await self.broadcast_to_livestream({
            "type": "chat_message_deleted",
            "message_id": message_id
        })
        return True

    async def edit_chat_message(self, message_id: str, new_text: str) -> bool:
        """Modifier le texte d'un message. Broadcaster l'événement."""
        for msg in self.chat_messages:
            if msg['id'] == message_id:
                msg['text'] = new_text
                msg['edited'] = True
                await self.broadcast_to_livestream({
                    "type": "chat_message_edited",
                    "message_id": message_id,
                    "text": new_text,
                })
                return True
        return False

    async def set_chat_open(self, open: bool) -> None:
        """Ouvrir ou fermer le chat (admin). Broadcaster l'état à toutes les connexions."""
        self.chat_open = open
        # Broadcaster à toutes les connexions actives (pas seulement les spectateurs livestream)
        # pour s'assurer que tous reçoivent le changement d'état
        await self.broadcast({
            "type": "chat_status",
            "open": open,
            "message": "Le chat est maintenant ouvert." if open else "Le chat a été fermé par l'administrateur."
        })

    async def clear_chat(self) -> None:
        """Vider tout le chat (admin)."""
        self.chat_messages.clear()
        self.hidden_message_ids.clear()
        await self.broadcast({
            "type": "chat_cleared",
            "message": "Le chat a été vidé par l'administrateur."
        })

    def get_chat_history(self, limit: int = 50) -> List[dict]:
        """Retourne les derniers messages visibles."""
        visible = self._visible_messages()
        return visible[-limit:]

    def get_chat_state(self) -> dict:
        """Retourne l'état complet du chat (pour un nouveau connecté)."""
        return {
            "type": "chat_init",
            "open": self.chat_open,
            "messages": self.get_chat_history(50),
            "viewers": self.get_livestream_viewer_count(),
        }


    # ── Méthodes Comments temps réel ─────────────────────────────────────────

    def _comment_room_key(self, content_type: str, content_id: str) -> str:
        return f"{content_type}:{content_id}"

    async def join_comments(self, websocket: WebSocket, content_type: str, content_id: str):
        """Abonner une connexion aux commentaires d'un contenu"""
        if not hasattr(self, 'comment_rooms'):
            self.comment_rooms: Dict[str, List[WebSocket]] = {}
        key = self._comment_room_key(content_type, content_id)
        if key not in self.comment_rooms:
            self.comment_rooms[key] = []
        if websocket not in self.comment_rooms[key]:
            self.comment_rooms[key].append(websocket)

    def leave_comments(self, websocket: WebSocket, content_type: str = None, content_id: str = None):
        """Désabonner une connexion (d'une room ou de toutes)"""
        if not hasattr(self, 'comment_rooms'):
            return
        if content_type and content_id:
            key = self._comment_room_key(content_type, content_id)
            if key in self.comment_rooms and websocket in self.comment_rooms[key]:
                self.comment_rooms[key].remove(websocket)
        else:
            for connections in self.comment_rooms.values():
                if websocket in connections:
                    connections.remove(websocket)

    async def broadcast_comment_event(self, content_type: str, content_id: str, event: dict):
        """Envoyer un événement commentaire à tous les abonnés de cette room"""
        if not hasattr(self, 'comment_rooms'):
            return
        key = self._comment_room_key(content_type, content_id)
        connections = self.comment_rooms.get(key, [])
        if not connections:
            return
        msg_str = json.dumps(event)
        dead = []
        for ws in connections:
            try:
                await ws.send_text(msg_str)
            except Exception:
                dead.append(ws)
        for ws in dead:
            connections.remove(ws)


# Instance globale du gestionnaire WebSocket
websocket_manager = WebSocketManager()
websocket_manager.comment_rooms: Dict[str, list] = {}
