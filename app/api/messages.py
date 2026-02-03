from fastapi import APIRouter, HTTPException, Depends
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.message import MessageCreate, MessageOut
from app.services.message_service import (
    send_message, get_message, get_inbox, get_sent_messages,
    get_conversation, mark_as_read, delete_message,
    count_unread_messages, get_all_messages
)
from typing import List

router = APIRouter()

@router.get("/")
async def list_all_messages(current_user=Depends(get_admin_user), skip: int = 0, limit: int = 1000):
    """Lister tous les messages (admin seulement)"""
    return await get_all_messages(skip, limit)

@router.post("/")
async def create_message(message: MessageCreate, current_user=Depends(get_current_user)):
    """Envoyer un message"""
    result = await send_message(str(current_user.id), message)
    if not result:
        raise HTTPException(status_code=404, detail="Destinataire introuvable")
    return result

@router.get("/inbox")
async def get_my_inbox(current_user=Depends(get_current_user), skip: int = 0, limit: int = 50):
    """Récupérer mes messages reçus"""
    return await get_inbox(str(current_user.id), skip, limit)

@router.get("/sent")
async def get_my_sent(current_user=Depends(get_current_user), skip: int = 0, limit: int = 50):
    """Récupérer mes messages envoyés"""
    return await get_sent_messages(str(current_user.id), skip, limit)

@router.get("/unread/count")
async def count_unread(current_user=Depends(get_current_user)):
    """Compter mes messages non lus"""
    count = await count_unread_messages(str(current_user.id))
    return {"count": count}

@router.get("/conversation/{other_user_id}")
async def get_conversation_api(other_user_id: str, current_user=Depends(get_current_user), skip: int = 0, limit: int = 50):
    """Récupérer la conversation avec un utilisateur"""
    return await get_conversation(str(current_user.id), other_user_id, skip, limit)

@router.get("/{message_id}")
async def get_one_message(message_id: str, current_user=Depends(get_current_user)):
    """Récupérer un message par ID"""
    message = await get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message introuvable")
    
    # Vérifier que l'utilisateur est l'expéditeur ou le destinataire
    if message.sender_id != str(current_user.id) and message.receiver_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return message

@router.patch("/{message_id}/read")
async def mark_message_read(message_id: str, current_user=Depends(get_current_user)):
    """Marquer un message comme lu"""
    message = await mark_as_read(message_id, str(current_user.id))
    if not message:
        raise HTTPException(status_code=404, detail="Message introuvable ou non autorisé")
    return message

@router.delete("/{message_id}")
async def remove_message(message_id: str, current_user=Depends(get_current_user)):
    """Supprimer un message"""
    ok = await delete_message(message_id, str(current_user.id))
    if not ok:
        raise HTTPException(status_code=404, detail="Message introuvable ou non autorisé")
    return {"ok": True}
