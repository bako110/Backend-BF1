from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from app.utils.auth import get_current_user, get_admin_user
from app.schemas.user import UserCreate, UserOut, UserLoginSchema, UserLocationUpdate, FcmTokenUpdate
from app.services.user_service import create_user, get_user, list_users, login_user_service, set_user_active, delete_user
from app.models.user import User
from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import secrets
import os
import urllib.parse
import json
import httpx
from jose import jwt as jose_jwt

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://bf1.fly.dev/api/v1/users/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://bf1-tv-mobile.onrender.com")

FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "https://bf1.fly.dev/api/v1/users/auth/facebook/callback")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme")
ALGORITHM = "HS256"
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    """
    Demande de réinitialisation du mot de passe par email.
    Retourne toujours 200 pour ne pas révéler l'existence d'un compte.
    """
    user = await User.find_one({"email": data.email})
    if user:
        # Générer un token sécurisé (32 bytes hex)
        reset_token = secrets.token_urlsafe(32)
        # Stocker le token en attendant l'envoi email (à connecter à un service email)
        import datetime as dt
        user.reset_token = reset_token
        user.reset_token_expires = dt.datetime.utcnow() + dt.timedelta(hours=2)
        await user.save()
        # TODO: Envoyer l'email via votre service (SendGrid, SMTP, etc.)
        # Exemple: await send_reset_email(user.email, reset_token)
        print(f"[ForgotPassword] Token pour {user.email}: {reset_token}")

    # Toujours 200 pour ne pas divulguer l'existence du compte
    return {"message": "Si cet email est associé à un compte, vous recevrez un lien de réinitialisation."}

@router.post("/register")
async def register_user(user: UserCreate):
    """Créer un nouveau compte utilisateur et le connecter automatiquement"""
    if len(user.password) > 72:
        raise HTTPException(status_code=400, detail="Le mot de passe ne doit pas dépasser 72 caractères.")
    
    # Créer l'utilisateur
    created_user = await create_user(user)
    
    # Connecter automatiquement l'utilisateur après inscription
    login_result = await login_user_service(user.username, user.password)
    
    return login_result

@router.post("/login")
async def login_user(data: UserLoginSchema):
    """Connexion avec email, username ou téléphone"""
    result = await login_user_service(data.identifier, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Identifiants invalides")
    return result

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Récupérer les informations de l'utilisateur connecté"""
    return current_user

@router.patch("/me/location", response_model=UserOut)
async def update_user_location(location: UserLocationUpdate, current_user=Depends(get_current_user)):
    """Mettre à jour la localisation de l'utilisateur connecté"""
    print(f"📍 [API] Mise à jour localisation pour {current_user.username}")
    print(f"📍 [API] Données reçues: {location.dict()}")
    
    # Mettre à jour les champs de localisation
    if location.country_code is not None:
        current_user.location_country_code = location.country_code
        print(f"  ✓ country_code: {location.country_code}")
    if location.is_in_country is not None:
        current_user.location_is_in_country = location.is_in_country
        print(f"  ✓ is_in_country: {location.is_in_country}")
    if location.latitude is not None:
        current_user.location_latitude = location.latitude
        print(f"  ✓ latitude: {location.latitude}")
    if location.longitude is not None:
        current_user.location_longitude = location.longitude
        print(f"  ✓ longitude: {location.longitude}")
    
    current_user.location_updated_at = datetime.utcnow()
    current_user.updated_at = datetime.utcnow()
    
    await current_user.save()
    print(f"✅ [API] Localisation enregistrée pour {current_user.username}")
    
    return current_user

@router.post("/fcm-token")
async def save_fcm_token(body: FcmTokenUpdate, current_user=Depends(get_current_user)):
    """Enregistrer ou mettre à jour le token FCM Firebase de l'utilisateur"""
    token = body.fcm_token.strip()
    if not token:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Token FCM invalide")

    # Ajouter le token s'il n'est pas déjà présent (évite les doublons)
    if not hasattr(current_user, 'fcm_tokens') or current_user.fcm_tokens is None:
        current_user.fcm_tokens = []
    if token not in current_user.fcm_tokens:
        current_user.fcm_tokens.append(token)
        current_user.updated_at = datetime.utcnow()
        await current_user.save()
        print(f"✅ Token FCM enregistré pour {current_user.username} [{body.platform}]")

    return {"status": "ok"}


@router.delete("/fcm-token")
async def remove_fcm_token(body: FcmTokenUpdate, current_user=Depends(get_current_user)):
    """Supprimer un token FCM (déconnexion / désactivation des notifs)"""
    token = body.fcm_token.strip()
    if hasattr(current_user, 'fcm_tokens') and current_user.fcm_tokens:
        current_user.fcm_tokens = [t for t in current_user.fcm_tokens if t != token]
        current_user.updated_at = datetime.utcnow()
        await current_user.save()
    return {"status": "ok"}


@router.get("/me/location")
async def get_user_location(current_user=Depends(get_current_user)):
    """Récupérer la localisation de l'utilisateur connecté"""
    return {
        "username": current_user.username,
        "country_code": current_user.location_country_code,
        "is_in_country": current_user.location_is_in_country,
        "latitude": current_user.location_latitude,
        "longitude": current_user.location_longitude,
        "updated_at": current_user.location_updated_at,
        "price_multiplier": 1 if current_user.location_is_in_country else 3
    }

# ─────────────────────────────────────────────────────────────
# Google OAuth 2.0  (must be declared BEFORE /{user_id})
# ─────────────────────────────────────────────────────────────

@router.get("/auth/google")
async def google_auth_redirect():
    """Redirect browser to Google OAuth consent screen."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google OAuth non configuré (GOOGLE_CLIENT_ID manquant)")
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url=url)


@router.get("/auth/google/callback")
async def google_auth_callback(code: str = None, error: str = None):
    """Exchange Google auth code for user info, create/find user, issue JWT."""
    if error or not code:
        error_url = f"{FRONTEND_URL}/pages/connexion.html?auth_error=access_denied"
        return RedirectResponse(url=error_url)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Exchange code → access_token
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_resp.json()
            access_token_google = token_data.get("access_token")
            if not access_token_google:
                raise ValueError(f"Pas d'access_token Google: {token_data}")

            # Get user info from Google
            userinfo_resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token_google}"},
            )
            userinfo = userinfo_resp.json()

        email = userinfo.get("email", "").lower().strip()
        google_sub = userinfo.get("sub", "")
        given_name = userinfo.get("given_name", "")
        family_name = userinfo.get("family_name", "")
        full_name = (f"{given_name}_{family_name}".strip("_") or email.split("@")[0]).replace(" ", "_")

        if not email:
            raise ValueError("Email non reçu de Google")

        # Find or create user
        user = await User.find_one({"email": email})
        if not user:
            # Build a unique username
            base_username = full_name[:20] or email.split("@")[0]
            username = base_username
            if await User.find_one({"username": username}):
                username = f"{base_username}_{google_sub[-6:]}"

            fake_password = secrets.token_hex(32)
            user = User(
                email=email,
                username=username,
                hashed_password=_pwd_context.hash(fake_password),
            )
            await user.insert()
            print(f"[GoogleOAuth] Nouvel utilisateur créé: {username} ({email})")
        else:
            print(f"[GoogleOAuth] Utilisateur existant: {user.username} ({email})")

        # Emit welcome notification for new users
        try:
            from app.services.notification_service import send_welcome_notification
            await send_welcome_notification(str(user.id), user.username)
        except Exception:
            pass

        # Issue our JWT
        payload = {"sub": str(user.id)}
        bf1_token = jose_jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        user_data = json.dumps({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_premium": user.is_premium,
            "is_active": user.is_active,
        })

        # Rediriger vers le deep link de l'app mobile : bf1tv://oauth/callback?token=xxx
        # Android intercepte ce schéma via onNewIntent dans MainActivity
        deep_link = (
            f"bf1tv://oauth/callback"
            f"?token={urllib.parse.quote(bf1_token)}"
            f"&user={urllib.parse.quote(user_data)}"
        )
        return RedirectResponse(url=deep_link)

    except Exception as exc:
        print(f"[GoogleOAuth] Erreur callback: {exc}")
        return RedirectResponse(url="bf1tv://oauth/callback?error=server_error")


# Facebook OAuth 2.0
# ─────────────────────────────────────────────────────────────

@router.get("/auth/facebook")
async def facebook_auth_redirect():
    """Redirect browser to Facebook OAuth consent screen."""
    if not FACEBOOK_APP_ID:
        raise HTTPException(status_code=503, detail="Facebook OAuth non configuré (FACEBOOK_APP_ID manquant)")
    params = {
        "client_id": FACEBOOK_APP_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "scope": "public_profile,email",
        "response_type": "code",
    }
    url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
    return RedirectResponse(url=url)


@router.get("/auth/facebook/callback")
async def facebook_auth_callback(code: str = None, error: str = None, error_reason: str = None):
    """Exchange Facebook auth code for user info, create/find user, issue JWT."""
    if error or not code:
        error_url = f"{FRONTEND_URL}/pages/connexion.html?auth_error=access_denied"
        return RedirectResponse(url=error_url)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Exchange code → access_token
            token_resp = await client.get(
                "https://graph.facebook.com/v19.0/oauth/access_token",
                params={
                    "client_id": FACEBOOK_APP_ID,
                    "client_secret": FACEBOOK_APP_SECRET,
                    "redirect_uri": FACEBOOK_REDIRECT_URI,
                    "code": code,
                },
            )
            token_data = token_resp.json()
            access_token_fb = token_data.get("access_token")
            if not access_token_fb:
                raise ValueError(f"Pas d'access_token Facebook: {token_data}")

            # Get user info from Facebook
            userinfo_resp = await client.get(
                "https://graph.facebook.com/me",
                params={"fields": "id,name,email", "access_token": access_token_fb},
            )
            userinfo = userinfo_resp.json()

        fb_id = userinfo.get("id", "")
        full_name = userinfo.get("name", "").replace(" ", "_")
        email = userinfo.get("email", "").lower().strip()

        # Facebook may not provide email (phone-only accounts)
        if not email:
            email = f"fb_{fb_id}@noemail.bf1tv"

        # Find or create user
        user = await User.find_one({"email": email})
        if not user:
            base_username = full_name[:20] or f"fb_{fb_id}"
            username = base_username
            if await User.find_one({"username": username}):
                username = f"{base_username}_{fb_id[-6:]}"

            fake_password = secrets.token_hex(32)
            user = User(
                email=email,
                username=username,
                hashed_password=_pwd_context.hash(fake_password),
            )
            await user.insert()
            print(f"[FacebookOAuth] Nouvel utilisateur créé: {username} ({email})")
        else:
            print(f"[FacebookOAuth] Utilisateur existant: {user.username} ({email})")

        # Emit welcome notification for new users
        try:
            from app.services.notification_service import send_welcome_notification
            await send_welcome_notification(str(user.id), user.username)
        except Exception:
            pass

        # Issue our JWT
        payload = {"sub": str(user.id)}
        bf1_token = jose_jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        user_data = json.dumps({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_premium": user.is_premium,
            "is_active": user.is_active,
        })

        redirect_url = (
            f"{FRONTEND_URL}/pages/auth-callback.html"
            f"?token={urllib.parse.quote(bf1_token)}"
            f"&user={urllib.parse.quote(user_data)}"
        )
        return RedirectResponse(url=redirect_url)

    except Exception as exc:
        print(f"[FacebookOAuth] Erreur callback: {exc}")
        error_url = f"{FRONTEND_URL}/pages/connexion.html?auth_error=server_error"
        return RedirectResponse(url=error_url)


@router.get("", response_model=List[UserOut])
async def get_all_users(current_user=Depends(get_admin_user)):
    """Lister tous les utilisateurs (admin seulement)"""
    return await list_users()

@router.get("/{user_id}", response_model=UserOut)
async def get_one_user(user_id: str, current_user=Depends(get_current_user)):
    """Récupérer un utilisateur par ID"""
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.patch("/{user_id}/ban", response_model=UserOut)
async def ban_user(user_id: str, current_user=Depends(get_admin_user)):
    """Bannir un utilisateur (admin seulement)"""
    user = await set_user_active(user_id, False)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.patch("/{user_id}/unban", response_model=UserOut)
async def unban_user(user_id: str, current_user=Depends(get_admin_user)):
    """Débannir un utilisateur (admin seulement)"""
    user = await set_user_active(user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.delete("/{user_id}")
async def delete_one_user(user_id: str, current_user=Depends(get_admin_user)):
    """Supprimer un utilisateur (admin seulement)"""
    deleted = await delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return {"ok": True}
