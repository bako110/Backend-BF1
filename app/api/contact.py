from fastapi import APIRouter, status, Depends
from app.utils.auth import get_current_user
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

router = APIRouter()

class ContactMessage(BaseModel):
	name: str = Field(..., min_length=2, max_length=100)
	email: EmailStr
	message: str = Field(..., min_length=10, max_length=1000)
	subject: Optional[str] = Field(None, max_length=200)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def send_contact_message(msg: ContactMessage):
	"""Envoyer un message de contact"""
	# TODO: Envoyer un email ou stocker en base
	return {
		"success": True,
		"message": "Votre message a bien été envoyé. Nous vous répondrons rapidement."
	}

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
