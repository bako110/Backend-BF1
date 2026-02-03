from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.schemas.token import Token
from app.models.user import User
from typing import Optional
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")
ALGORITHM = "HS256"
from fastapi.security import APIKeyHeader
oauth2_scheme = APIKeyHeader(name="Authorization")
optional_oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Extraire le token du format "Bearer <token>"
        if token.startswith("Bearer "):
            token = token[7:]  # Enlever "Bearer "
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_oauth2_scheme)) -> Optional[User]:
    """Permet l'accès avec ou sans authentification (pour les endpoints publics)"""
    if credentials is None:
        return None
    
    token = credentials.credentials
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user = await User.get(user_id)
        return user
    except (JWTError, Exception):
        return None
