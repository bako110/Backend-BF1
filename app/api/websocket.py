from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel
from app.services.websocket_service import websocket_manager
from app.utils.auth import get_admin_user, get_current_user
import json


class EditMessageBody(BaseModel):
    text: str

router = APIRouter()


# ── WebSocket principal ────────────────────────────────────────────────────────

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket principal : notifications push + chat live"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                mtype = msg.get("type")

                # ── Ping/pong keepalive ──
                if mtype == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))

                # ── Rejoindre le livestream ──
                elif mtype == "join_livestream":
                    user_id = msg.get("user_id")
                    await websocket_manager.join_livestream(websocket, user_id)
                    # Envoyer l'historique chat + état du chat au nouvel arrivant
                    await websocket.send_text(json.dumps({
                        **websocket_manager.get_chat_state(),
                        "type": "joined_livestream",
                        "total_viewers": websocket_manager.get_livestream_viewer_count(),
                    }))

                # ── Quitter le livestream ──
                elif mtype == "leave_livestream":
                    user_id = msg.get("user_id")
                    await websocket_manager.leave_livestream(websocket, user_id)
                    await websocket.send_text(json.dumps({
                        "type": "left_livestream",
                        "total_viewers": websocket_manager.get_livestream_viewer_count(),
                    }))

                # ── Envoyer un message chat ──
                elif mtype == "chat_send":
                    text     = (msg.get("text") or "").strip()
                    username = (msg.get("username") or "Anonyme").strip()
                    user_id  = msg.get("user_id")
                    avatar   = msg.get("avatar_url")

                    if not text:
                        await websocket.send_text(json.dumps({"type": "error", "code": "EMPTY_MESSAGE"}))
                        continue
                    if len(text) > 300:
                        await websocket.send_text(json.dumps({"type": "error", "code": "MESSAGE_TOO_LONG"}))
                        continue

                    result = await websocket_manager.add_chat_message(user_id, username, avatar, text)
                    if result is None:
                        await websocket.send_text(json.dumps({
                            "type": "error", "code": "CHAT_CLOSED",
                            "message": "Le chat est actuellement fermé."
                        }))

                # ── Commandes admin ──
                elif mtype == "admin_hide_message":
                    if not _check_admin_token(msg.get("token")):
                        await websocket.send_text(json.dumps({"type": "error", "code": "UNAUTHORIZED"}))
                        continue
                    await websocket_manager.hide_chat_message(msg["message_id"])

                elif mtype == "admin_delete_message":
                    if not _check_admin_token(msg.get("token")):
                        await websocket.send_text(json.dumps({"type": "error", "code": "UNAUTHORIZED"}))
                        continue
                    await websocket_manager.delete_chat_message(msg["message_id"])

                elif mtype == "admin_set_chat_open":
                    if not _check_admin_token(msg.get("token")):
                        await websocket.send_text(json.dumps({"type": "error", "code": "UNAUTHORIZED"}))
                        continue
                    await websocket_manager.set_chat_open(bool(msg.get("open", True)))

                elif mtype == "admin_clear_chat":
                    if not _check_admin_token(msg.get("token")):
                        await websocket.send_text(json.dumps({"type": "error", "code": "UNAUTHORIZED"}))
                        continue
                    await websocket_manager.clear_chat()

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/comments/{content_type}/{content_id}")
async def comments_websocket(websocket: WebSocket, content_type: str, content_id: str):
    """WebSocket temps réel pour les commentaires d'un contenu"""
    await websocket.accept()
    await websocket_manager.join_comments(websocket, content_type, content_id)
    # Envoyer les commentaires initiaux
    try:
        from app.services.comment_service import get_comments
        initial = await get_comments(content_id, content_type, skip=0, limit=50)
        await websocket.send_text(json.dumps({
            "type": "comments_init",
            "comments": [_serialize(c) for c in initial],
        }))
    except Exception as e:
        print(f"❌ Erreur init commentaires WS: {e}")

    try:
        while True:
            await websocket.receive_text()  # keepalive — on ignore les messages entrants
    except WebSocketDisconnect:
        websocket_manager.leave_comments(websocket, content_type, content_id)
    except Exception:
        websocket_manager.leave_comments(websocket, content_type, content_id)


def _serialize(obj) -> dict:
    """Convertit un objet Beanie/dict en dict JSON-serializable"""
    if isinstance(obj, dict):
        d = obj
    else:
        d = obj.dict() if hasattr(obj, 'dict') else vars(obj)
    result = {}
    for k, v in d.items():
        if hasattr(v, '__str__') and not isinstance(v, (str, int, float, bool, type(None), list, dict)):
            result[k] = str(v)
        else:
            result[k] = v
    return result


def _check_admin_token(token: str) -> bool:
    """Vérification légère du token admin via JWT pour les commandes WS"""
    if not token:
        return False
    try:
        from app.utils.auth import decode_token
        payload = decode_token(token)
        return payload is not None
    except Exception:
        return False


# ── REST endpoints admin pour modération ─────────────────────────────────────

@router.get("/ws/status")
async def websocket_status():
    return {
        "active_connections": await websocket_manager.get_connection_count(),
        "livestream_viewers": websocket_manager.get_livestream_viewer_count(),
        "chat_open": websocket_manager.chat_open,
        "chat_messages_count": len(websocket_manager.chat_messages),
        "status": "running",
    }


@router.get("/ws/chat/messages")
async def get_chat_messages(current_user=Depends(get_admin_user)):
    """Admin : récupérer tous les messages (y compris masqués)"""
    return {
        "messages": websocket_manager.chat_messages,
        "hidden_ids": list(websocket_manager.hidden_message_ids),
        "chat_open": websocket_manager.chat_open,
        "total": len(websocket_manager.chat_messages),
    }


@router.post("/ws/chat/hide/{message_id}")
async def hide_message(message_id: str, current_user=Depends(get_admin_user)):
    """Admin : masquer un message"""
    await websocket_manager.hide_chat_message(message_id)
    return {"ok": True, "message_id": message_id, "action": "hidden"}


@router.delete("/ws/chat/delete/{message_id}")
async def delete_message(message_id: str, current_user=Depends(get_admin_user)):
    """Admin : supprimer définitivement un message"""
    await websocket_manager.delete_chat_message(message_id)
    return {"ok": True, "message_id": message_id, "action": "deleted"}


@router.post("/ws/chat/open")
async def open_chat(current_user=Depends(get_admin_user)):
    """Admin : ouvrir le chat"""
    await websocket_manager.set_chat_open(True)
    return {"ok": True, "chat_open": True}


@router.post("/ws/chat/close")
async def close_chat(current_user=Depends(get_admin_user)):
    """Admin : fermer le chat"""
    await websocket_manager.set_chat_open(False)
    return {"ok": True, "chat_open": False}


@router.delete("/ws/chat/clear")
async def clear_chat(current_user=Depends(get_admin_user)):
    """Admin : vider tout le chat"""
    await websocket_manager.clear_chat()
    return {"ok": True, "action": "cleared"}


# ── Endpoints utilisateur (propres messages) ──────────────────────────────────

@router.delete("/ws/chat/my/{message_id}")
async def user_delete_own_message(message_id: str, current_user=Depends(get_current_user)):
    """User : supprimer son propre message chat"""
    user_id = str(current_user.id)
    msg = next((m for m in websocket_manager.chat_messages if m['id'] == message_id), None)
    if not msg:
        raise HTTPException(status_code=404, detail="Message introuvable")
    if str(msg.get("user_id")) != user_id:
        raise HTTPException(status_code=403, detail="Ce message ne vous appartient pas")
    await websocket_manager.delete_chat_message(message_id)
    return {"ok": True, "message_id": message_id}


@router.patch("/ws/chat/my/{message_id}")
async def user_edit_own_message(message_id: str, body: EditMessageBody, current_user=Depends(get_current_user)):
    """User : modifier son propre message chat"""
    user_id = str(current_user.id)
    new_text = body.text.strip()
    if not new_text or len(new_text) > 300:
        raise HTTPException(status_code=400, detail="Texte invalide")
    msg = next((m for m in websocket_manager.chat_messages if m['id'] == message_id), None)
    if not msg:
        raise HTTPException(status_code=404, detail="Message introuvable")
    if str(msg.get("user_id")) != user_id:
        raise HTTPException(status_code=403, detail="Ce message ne vous appartient pas")
    await websocket_manager.edit_chat_message(message_id, new_text)
    return {"ok": True, "message_id": message_id, "text": new_text}
