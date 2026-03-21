from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from app.services.websocket_service import websocket_manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket pour les notifications push en temps réel"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Garder la connexion ouverte et écouter les messages
            data = await websocket.receive_text()
            
            # Traiter les messages reçus du client si nécessaire
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "subscribe":
                    # Gérer les abonnements à des types de notifications spécifiques
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "notification_types": message.get("notification_types", [])
                    }))
                elif message.get("type") == "join_livestream":
                    # L'utilisateur rejoint le livestream
                    user_id = message.get("user_id")  # Optionnel, peut être None pour visiteurs anonymes
                    await websocket_manager.join_livestream(websocket, user_id)
                    await websocket.send_text(json.dumps({
                        "type": "joined_livestream",
                        "status": "success",
                        "total_viewers": websocket_manager.get_livestream_viewer_count()
                    }))
                elif message.get("type") == "leave_livestream":
                    # L'utilisateur quitte le livestream
                    user_id = message.get("user_id")
                    await websocket_manager.leave_livestream(websocket, user_id)
                    await websocket.send_text(json.dumps({
                        "type": "left_livestream", 
                        "status": "success",
                        "total_viewers": websocket_manager.get_livestream_viewer_count()
                    }))
            except json.JSONDecodeError:
                # Message non-JSON, ignorer
                pass
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        websocket_manager.disconnect(websocket)

@router.get("/ws/status")
async def websocket_status():
    """Endpoint pour vérifier le statut des connexions WebSocket"""
    return {
        "active_connections": await websocket_manager.get_connection_count(),
        "status": "running"
    }
