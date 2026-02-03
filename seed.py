"""
Script pour exécuter le peuplement de la base de données
Usage: python seed.py
"""
import asyncio
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import User
from app.models.show import Show
from app.models.movie import Movie
from app.models.news import News
from app.models.comment import Comment
from app.models.like import Like
from app.models.favorite import Favorite
from app.utils.seed_data import seed_all
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

async def init_db():
    """Initialiser la connexion à la base de données"""
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/Bf1_db")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "Bf1_db")
    
    print(f"🔌 Connexion à MongoDB: {MONGODB_URL}")
    print(f"📦 Base de données: {DATABASE_NAME}\n")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[User, Show, Movie, News, Comment, Like, Favorite]
    )
    
    print("✅ Connexion à la base de données établie\n")


async def main():
    """Fonction principale"""
    try:
        await init_db()
        await seed_all()
    except Exception as e:
        print(f"\n❌ Erreur lors du peuplement: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 SCRIPT DE PEUPLEMENT BF1 TV")
    print("=" * 60)
    asyncio.run(main())
    print("\n" + "=" * 60)
