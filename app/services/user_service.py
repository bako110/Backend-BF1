

from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(data: UserCreate) -> User:
	# Vérifier si l'email existe déjà
	if data.email:
		existing_email = await User.find_one({"email": data.email})
		if existing_email:
			from fastapi import HTTPException
			raise HTTPException(
				status_code=400,
				detail="Cet email est déjà utilisé. Veuillez en choisir un autre."
			)
	
	# Vérifier si le username existe déjà
	existing_username = await User.find_one({"username": data.username})
	if existing_username:
		from fastapi import HTTPException
		raise HTTPException(
			status_code=400,
			detail="Ce nom d'utilisateur est déjà pris. Veuillez en choisir un autre."
		)
	
	# Vérifier si le téléphone existe déjà (si fourni)
	if data.phone:
		existing_phone = await User.find_one({"phone": data.phone})
		if existing_phone:
			from fastapi import HTTPException
			raise HTTPException(
				status_code=400,
				detail="Ce numéro de téléphone est déjà utilisé."
			)
	
	password = data.password[:72] if data.password else ""
	hashed_password = pwd_context.hash(password)
	user = User(
		email=data.email,
		username=data.username,
		phone=data.phone,
		hashed_password=hashed_password,
	)
	await user.insert()
	
	# Envoyer une notification de bienvenue
	try:
		from app.services.notification_service import send_welcome_notification
		await send_welcome_notification(str(user.id), user.username)
	except Exception as e:
		print(f"⚠️ Erreur envoi notification bienvenue: {e}")
	
	return user

async def get_user(user_id: str) -> Optional[User]:
	return await User.get(user_id)


async def list_users() -> List[User]:
	return await User.find_all().to_list()


async def set_user_active(user_id: str, is_active: bool) -> Optional[User]:
	user = await User.get(user_id)
	if not user:
		return None
	user.is_active = is_active
	user.updated_at = datetime.utcnow()
	await user.save()
	return user


async def delete_user(user_id: str) -> bool:
	user = await User.get(user_id)
	if not user:
		return False
	await user.delete()
	return True

from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")
ALGORITHM = "HS256"

async def login_user_service(identifier: str, password: str):
	print(f"🔐 Tentative de connexion avec: {identifier}")
	# Recherche par email, username ou phone
	user = await User.find_one({
		"$or": [
			{"email": identifier},
			{"username": identifier},
			{"phone": identifier}
		]
	})
	if not user:
		print(f"❌ Utilisateur non trouvé: {identifier}")
		return None
	
	print(f"✅ Utilisateur trouvé: {user.username} (email: {user.email})")
	print(f"🔑 Vérification du mot de passe...")
	
	# Vérification du mot de passe hashé
	if not pwd_context.verify(password, user.hashed_password):
		print(f"❌ Mot de passe incorrect pour {user.username}")
		return None
	
	print(f"✅ Mot de passe correct pour {user.username}")
	# Génération d'un JWT réel
	payload = {"sub": str(user.id)}
	token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
	user_out = UserOut(
		id=str(user.id),
		email=user.email,
		phone=user.phone,
		username=user.username,
		is_active=user.is_active,
		is_premium=user.is_premium,
		favorites=getattr(user, "favorites", []),
		created_at=user.created_at,
		updated_at=user.updated_at
	)
	return {"access_token": token, "token_type": "bearer", "user": user_out}
