#!/usr/bin/env python3
"""
Script pour tester le WebSocket du backend BF1
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://154.66.167.241:8000/ws"
    
    try:
        print(f"🔌 Connexion à {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connecté au WebSocket!")
            
            # Envoyer un message de souscription
            subscribe_msg = {
                "type": "subscribe",
                "notification_types": ["popular_program", "flash_info", "daily_news"]
            }
            await websocket.send(json.dumps(subscribe_msg))
            print("📤 Message de souscription envoyé")
            
            # Écouter les messages
            print("👂 En attente de messages...")
            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"📱 Message reçu: {data}")
                    
                    if data.get("type") == "push_notification":
                        print(f"🔔 Notification: {data.get('data')}")
                        
            except websockets.exceptions.ConnectionClosed:
                print("❌ Connexion fermée")
                
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
