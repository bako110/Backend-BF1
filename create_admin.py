
import asyncio
from app.models.user import User
from passlib.context import CryptContext
from app.config import init_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    await init_db()
    print("Création d'un administrateur :")
    nom = input("Nom d'utilisateur : ")
    prenom = input("Prénom (optionnel) : ")
    email = input("Email : ")
    phone = input("Téléphone (optionnel) : ")
    password = input("Mot de passe : ")
    print(f"Mot de passe saisi : {password}")
    hashed_password = pwd_context.hash(password[:72])
    print(f"Hash généré : {hashed_password}")
    user = User(
        username=nom,
        email=email,
        phone=phone if phone else None,
        hashed_password=hashed_password,
        is_admin=True,
        is_active=True,
        is_premium=False,
    )
    await user.insert()
    print(f"Administrateur {nom} créé avec succès.")

if __name__ == "__main__":
    asyncio.run(create_admin())
