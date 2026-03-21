"""
Script de migration pour ajouter le champ required_subscription_category
aux Archives, Films et Séries existants
"""
import asyncio
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.archive import Archive
from app.models.movie import Movie
from app.models.series import Series

# Configuration MongoDB
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bf1_db_dev")
DATABASE_NAME = "bf1_db_dev"

async def migrate_content():
    """Migrer les contenus existants pour ajouter required_subscription_category"""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(MONGODB_URI)
    database = client[DATABASE_NAME]
    
    # Initialiser Beanie
    await init_beanie(
        database=database,
        document_models=[Archive, Movie, Series]
    )
    
    print("🚀 Début de la migration des contenus...")
    
    # ===== MIGRATION DES ARCHIVES =====
    print("\n📦 Migration des Archives...")
    archives = await Archive.find_all().to_list()
    updated_archives = 0
    
    for archive in archives:
        # Si le champ n'existe pas ou est None, le définir
        if not hasattr(archive, 'required_subscription_category'):
            archive.required_subscription_category = None
            await archive.save()
            updated_archives += 1
            print(f"  ✅ Archive mise à jour: {archive.title}")
    
    print(f"✅ {updated_archives} archives mises à jour sur {len(archives)} au total")
    
    # ===== MIGRATION DES FILMS =====
    print("\n🎬 Migration des Films...")
    movies = await Movie.find_all().to_list()
    updated_movies = 0
    
    for movie in movies:
        # Si le champ n'existe pas ou est None, le définir
        if not hasattr(movie, 'required_subscription_category'):
            movie.required_subscription_category = None
            await movie.save()
            updated_movies += 1
            print(f"  ✅ Film mis à jour: {movie.title}")
    
    print(f"✅ {updated_movies} films mis à jour sur {len(movies)} au total")
    
    # ===== MIGRATION DES SÉRIES =====
    print("\n📺 Migration des Séries...")
    series_list = await Series.find_all().to_list()
    updated_series = 0
    
    for series in series_list:
        # Si le champ n'existe pas ou est None, le définir
        if not hasattr(series, 'required_subscription_category'):
            series.required_subscription_category = None
            await series.save()
            updated_series += 1
            print(f"  ✅ Série mise à jour: {series.title}")
    
    print(f"✅ {updated_series} séries mises à jour sur {len(series_list)} au total")
    
    # Résumé
    print(f"\n🎉 Migration terminée avec succès!")
    print(f"   - Archives: {updated_archives}/{len(archives)}")
    print(f"   - Films: {updated_movies}/{len(movies)}")
    print(f"   - Séries: {updated_series}/{len(series_list)}")
    print(f"\n💡 Les contenus ont maintenant le champ 'required_subscription_category' (null par défaut)")
    print(f"💡 Utilisez l'interface admin pour définir les catégories d'abonnement requises")

if __name__ == "__main__":
    asyncio.run(migrate_content())
