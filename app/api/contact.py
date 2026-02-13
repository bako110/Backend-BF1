from fastapi import APIRouter, status, Depends, HTTPException
from app.utils.auth import get_current_user, get_optional_user
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from beanie import Document
from bson import ObjectId

router = APIRouter()

# Modèle MongoDB pour stocker les messages de contact
class ContactMessageDoc(Document):
	name: str
	email: str
	message: str
	subject: Optional[str] = None
	created_at: datetime = Field(default_factory=datetime.utcnow)
	is_read: bool = False
	
	class Settings:
		name = "contact_messages"

# Schéma pour créer un message
class ContactMessageCreate(BaseModel):
	name: str = Field(..., min_length=2, max_length=100)
	email: EmailStr
	message: str = Field(..., min_length=10, max_length=1000)
	subject: Optional[str] = Field(None, max_length=200)

# Schéma pour la réponse
class ContactMessageOut(BaseModel):
	id: str
	name: str
	email: str
	message: str
	subject: Optional[str] = None
	created_at: datetime
	is_read: bool
	
	class Config:
		from_attributes = True

@router.post("/", status_code=status.HTTP_201_CREATED)
async def send_contact_message(msg: ContactMessageCreate):
	"""Envoyer un message de contact"""
	# Stocker le message en base de données
	contact_msg = ContactMessageDoc(**msg.dict())
	await contact_msg.insert()
	
	return {
		"success": True,
		"message": "Votre message a bien été envoyé. Nous vous répondrons rapidement."
	}

@router.get("/messages", response_model=List[ContactMessageOut])
async def get_contact_messages(skip: int = 0, limit: int = 100, current_user=Depends(get_optional_user)):
	"""Récupérer tous les messages de contact"""
	messages = await ContactMessageDoc.find_all().sort(-ContactMessageDoc.created_at).skip(skip).limit(limit).to_list()
	return [
		{
			"id": str(msg.id),
			"name": msg.name,
			"email": msg.email,
			"message": msg.message,
			"subject": msg.subject,
			"created_at": msg.created_at,
			"is_read": msg.is_read
		}
		for msg in messages
	]

@router.delete("/messages/{message_id}")
async def delete_contact_message(message_id: str, current_user=Depends(get_optional_user)):
	"""Supprimer un message de contact"""
	try:
		msg = await ContactMessageDoc.get(message_id)
		if not msg:
			raise HTTPException(status_code=404, detail="Message non trouvé")
		await msg.delete()
		return {"success": True, "message": "Message supprimé"}
	except Exception as e:
		raise HTTPException(status_code=404, detail="Message non trouvé")

@router.get("/about")
async def about_bf1():
	return {
		"name": "BF1 TV",
		"description": "Chaîne TV officielle BF1. Retrouvez le direct, les émissions, films, actualités et plus.",
		"website": "https://www.bf1tv.com",
		"support_email": "support@bf1tv.com",
		"socials": {
			"facebook": "https://facebook.com/bf1tv",
			"twitter": "https://twitter.com/bf1tv",
			"instagram": "https://instagram.com/bf1tv"
		}
	}
