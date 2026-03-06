from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        # Liste des connexions WebSocket actives
        self.active_connections: List[WebSocket] = []
        # Dictionnaire pour stocker les informations sur les connexions
        self.connection_info = {}
        # Tracking des utilisateurs regardant le livestream
        self.livestream_viewers: set = set()  # Set des IDs des utilisateurs regardant le live
        self.livestream_connections: List[WebSocket] = []  # Connexions actives pour le livestream
    
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

# Instance globale du gestionnaire WebSocket
websocket_manager = WebSocketManager()
