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

# Instance globale du gestionnaire WebSocket
websocket_manager = WebSocketManager()
