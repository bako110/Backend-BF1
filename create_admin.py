
import asyncio
from app.models.user import User
from passlib.context import CryptContext
from app.config import init_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    """Créer un administrateur par défaut"""
    await init_db()
    
    # Vérifier si un admin existe déjà
    existing_admin = await User.find_one(User.is_admin == True)
    # print(f"admin_existing":)
    if existing_admin:
        print(f"⚠️  Un administrateur existe déjà : {existing_admin.username}")
        print(f"   Email: {existing_admin.email}")
        return
    
    # Créer l'admin par défaut
    username = "admin"
    email = "admin@example.com"
    password = "password"
    
    print("🔧 Création de l'administrateur par défaut...")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    hashed_password = pwd_context.hash(password)
    
    user = User(
        username=username,
        email=email,
        phone=None,
        hashed_password=hashed_password,
        is_admin=True,
        is_active=True,
        is_premium=True,
    )
    
    await user.insert()
    print(f"✅ Administrateur créé avec succès!")
    print(f"\n📝 Identifiants de connexion:")
    print(f"   Username/Email: {username} ou {email}")
    print(f"   Password: {password}")
    print(f"\n⚠️  IMPORTANT: Changez ce mot de passe après la première connexion!")

if __name__ == "__main__":
    asyncio.run(create_admin())
