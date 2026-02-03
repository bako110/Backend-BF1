from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageUpdate
from typing import List, Optional, Dict
from datetime import datetime

async def send_message(sender_id: str, data: MessageCreate) -> Message:
    """Envoyer un message à un utilisateur"""
    # Vérifier que le destinataire existe
    receiver = await User.get(data.receiver_id)
    if not receiver:
        return None
    
    message = Message(
        sender_id=sender_id,
        receiver_id=data.receiver_id,
        subject=data.subject,
        content=data.content
    )
    await message.insert()
    return message

async def get_message(message_id: str) -> Optional[Message]:
    """Récupérer un message par ID"""
    return await Message.get(message_id)

async def get_inbox(user_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
    """Récupérer les messages reçus avec infos expéditeur"""
    messages = await Message.find(
        Message.receiver_id == user_id
    ).sort(-Message.created_at).skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos de l'expéditeur
    enriched_messages = []
    for msg in messages:
        sender = await User.get(msg.sender_id)
        msg_dict = msg.dict()
        msg_dict['sender_username'] = sender.username if sender else "Utilisateur inconnu"
        enriched_messages.append(msg_dict)
    
    return enriched_messages

async def get_sent_messages(user_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
    """Récupérer les messages envoyés avec infos destinataire"""
    messages = await Message.find(
        Message.sender_id == user_id
    ).sort(-Message.created_at).skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos du destinataire
    enriched_messages = []
    for msg in messages:
        receiver = await User.get(msg.receiver_id)
        msg_dict = msg.dict()
        msg_dict['receiver_username'] = receiver.username if receiver else "Utilisateur inconnu"
        enriched_messages.append(msg_dict)
    
    return enriched_messages

async def get_conversation(user_id: str, other_user_id: str, skip: int = 0, limit: int = 50) -> List[Dict]:
    """Récupérer la conversation entre deux utilisateurs"""
    messages = await Message.find(
        {
            "$or": [
                {"sender_id": user_id, "receiver_id": other_user_id},
                {"sender_id": other_user_id, "receiver_id": user_id}
            ]
        }
    ).sort(Message.created_at).skip(skip).limit(limit).to_list()
    
    return [msg.dict() for msg in messages]

async def mark_as_read(message_id: str, user_id: str) -> Optional[Message]:
    """Marquer un message comme lu (seulement par le destinataire)"""
    message = await Message.get(message_id)
    if not message or message.receiver_id != user_id:
        return None
    
    message.is_read = True
    message.read_at = datetime.utcnow()
    await message.save()
    return message

async def delete_message(message_id: str, user_id: str) -> bool:
    """Supprimer un message (expéditeur ou destinataire)"""
    message = await Message.get(message_id)
    if not message:
        return False
    
    if message.sender_id != user_id and message.receiver_id != user_id:
        return False
    
    await message.delete()
    return True

async def count_unread_messages(user_id: str) -> int:
    """Compter les messages non lus"""
    return await Message.find(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()

async def get_all_messages(skip: int = 0, limit: int = 1000) -> List[Dict]:
    """Récupérer tous les messages (pour admin)"""
    messages = await Message.find().skip(skip).limit(limit).to_list()
    
    # Enrichir avec les infos utilisateurs
    enriched_messages = []
    for msg in messages:
        sender = await User.get(msg.sender_id)
        receiver = await User.get(msg.receiver_id)
        msg_dict = msg.dict()
        msg_dict['sender_username'] = sender.username if sender else "Utilisateur inconnu"
        msg_dict['receiver_username'] = receiver.username if receiver else "Utilisateur inconnu"
        enriched_messages.append(msg_dict)
    
    return enriched_messages
