
from app.models.user import User
from app.utils.security import verify_password, hash_password
from app.utils.jwt import create_access_token
from typing import Optional


async def authenticate_user(identifier: str, password: str) -> Optional[User]:
	# identifier peut être email, username ou phone
	user = await User.find_one(
		(User.email == identifier) |
		(User.username == identifier) |
		(User.phone == identifier)
	)
	if not user or not verify_password(password, user.hashed_password):
		return None
	return user

async def login_user(identifier: str, password: str) -> Optional[str]:
	user = await authenticate_user(identifier, password)
	if not user:
		return None
	token = create_access_token({"sub": str(user.id), "email": user.email, "phone": user.phone, "username": user.username})
	return token
