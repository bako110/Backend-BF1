

from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from typing import List, Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(data: UserCreate) -> User:
	password = data.password[:72] if data.password else ""
	hashed_password = pwd_context.hash(password)
	user = User(
		email=data.email,
		username=data.username,
		phone=data.phone,
		hashed_password=hashed_password,
	)
	await user.insert()
	return user

async def get_user(user_id: str) -> Optional[User]:
	return await User.get(user_id)


async def list_users() -> List[User]:
	return await User.find_all().to_list()

from jose import jwt
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")
ALGORITHM = "HS256"

async def login_user_service(identifier: str, password: str):
	# Recherche par email, username ou phone
	user = await User.find_one({
		"$or": [
			{"email": identifier},
			{"username": identifier},
			{"phone": identifier}
		]
	})
	if not user:
		return None
	# Vérification du mot de passe hashé
	if not pwd_context.verify(password, user.hashed_password):
		return None
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
