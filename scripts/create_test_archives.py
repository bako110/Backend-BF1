"""
Script pour créer des archives de test dans la base de données
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.archive import Archive
from app.config import settings


async def create_test_archives():
    """Créer des archives de test"""
    
    # Connexion à MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[Archive]
    )
    
    print("🔗 Connecté à MongoDB")
    
    # Données de test
    test_archives = [
        {
            "title": "Interview exclusive avec Jean Dupont",
            "guest_name": "Jean Dupont",
            "guest_role": "Ministre de l'Économie",
            "description": "Une interview approfondie sur la politique économique du pays et les perspectives pour l'année à venir.",
            "duration_minutes": 45,
            "is_premium": True,
            "price": 4.99,
            "category": "Politique",
            "tags": ["économie", "politique", "gouvernement"],
            "archived_date": datetime.utcnow() - timedelta(days=30),
            "original_publish_date": datetime.utcnow() - timedelta(days=35),
            "rating": 4.5,
            "views": 1250,
            "image": "https://via.placeholder.com/800x450/1a1a1a/FFD700?text=Interview+Jean+Dupont",
            "thumbnail": "https://via.placeholder.com/400x225/1a1a1a/FFD700?text=Thumbnail",
            "video_url": "https://example.com/videos/interview-jean-dupont.mp4"
        },
        {
            "title": "Débat sur l'éducation nationale",
            "guest_name": "Marie Martin",
            "guest_role": "Experte en éducation",
            "description": "Discussion sur les réformes de l'éducation nationale et l'avenir de l'enseignement.",
            "duration_minutes": 60,
            "is_premium": True,
            "price": 5.99,
            "category": "Éducation",
            "tags": ["éducation", "réforme", "enseignement"],
            "archived_date": datetime.utcnow() - timedelta(days=20),
            "original_publish_date": datetime.utcnow() - timedelta(days=25),
            "rating": 4.2,
            "views": 890,
            "image": "https://via.placeholder.com/800x450/1a1a1a/FFD700?text=Débat+Éducation",
            "thumbnail": "https://via.placeholder.com/400x225/1a1a1a/FFD700?text=Thumbnail",
            "video_url": "https://example.com/videos/debat-education.mp4"
        },
        {
            "title": "Analyse de la crise sanitaire",
            "guest_name": "Dr. Pierre Santé",
            "guest_role": "Médecin épidémiologiste",
            "description": "Retour sur la gestion de la crise sanitaire et les leçons à en tirer pour l'avenir.",
            "duration_minutes": 50,
            "is_premium": True,
            "price": 3.99,
            "category": "Santé",
            "tags": ["santé", "covid", "épidémie"],
            "archived_date": datetime.utcnow() - timedelta(days=15),
            "original_publish_date": datetime.utcnow() - timedelta(days=18),
            "rating": 4.7,
            "views": 2100,
            "image": "https://via.placeholder.com/800x450/1a1a1a/FFD700?text=Crise+Sanitaire",
            "thumbnail": "https://via.placeholder.com/400x225/1a1a1a/FFD700?text=Thumbnail",
            "video_url": "https://example.com/videos/crise-sanitaire.mp4"
        },
        {
            "title": "L'avenir de la technologie",
            "guest_name": "Sophie Tech",
            "guest_role": "CEO TechCorp",
            "description": "Vision de l'avenir technologique et impact sur notre société.",
            "duration_minutes": 40,
            "is_premium": False,
            "price": 0.0,
            "category": "Technologie",
            "tags": ["tech", "innovation", "futur"],
            "archived_date": datetime.utcnow() - timedelta(days=10),
            "original_publish_date": datetime.utcnow() - timedelta(days=12),
            "rating": 4.8,
            "views": 3500,
            "image": "https://via.placeholder.com/800x450/1a1a1a/FFD700?text=Technologie",
            "thumbnail": "https://via.placeholder.com/400x225/1a1a1a/FFD700?text=Thumbnail",
            "video_url": "https://example.com/videos/avenir-tech.mp4"
        },
        {
            "title": "Culture et patrimoine",
            "guest_name": "Luc Culture",
            "guest_role": "Historien",
            "description": "Exploration du patrimoine culturel et son importance pour notre identité.",
            "duration_minutes": 55,
            "is_premium": True,
            "price": 4.49,
            "category": "Culture",
            "tags": ["culture", "patrimoine", "histoire"],
            "archived_date": datetime.utcnow() - timedelta(days=5),
            "original_publish_date": datetime.utcnow() - timedelta(days=8),
            "rating": 4.3,
            "views": 750,
            "image": "https://via.placeholder.com/800x450/1a1a1a/FFD700?text=Culture",
            "thumbnail": "https://via.placeholder.com/400x225/1a1a1a/FFD700?text=Thumbnail",
            "video_url": "https://example.com/videos/culture-patrimoine.mp4"
        }
    ]
    
    # Supprimer les archives existantes (optionnel)
    existing_count = await Archive.find().count()
    print(f"📊 Archives existantes: {existing_count}")
    
    # Créer les nouvelles archives
    created_count = 0
    for archive_data in test_archives:
        # Vérifier si l'archive existe déjà
        existing = await Archive.find_one({"title": archive_data["title"]})
        if existing:
            print(f"⚠️  Archive '{archive_data['title']}' existe déjà, ignorée")
            continue
        
        archive = Archive(**archive_data)
        await archive.insert()
        created_count += 1
        print(f"✅ Archive créée: {archive.title} (Premium: {archive.is_premium})")
    
    print(f"\n🎉 {created_count} archives de test créées avec succès!")
    print(f"📈 Total d'archives dans la base: {await Archive.find().count()}")
    
    # Afficher les catégories
    archives = await Archive.find().to_list()
    categories = list(set(a.category for a in archives if a.category))
    print(f"📂 Catégories disponibles: {', '.join(sorted(categories))}")


if __name__ == "__main__":
    print("🚀 Création d'archives de test...\n")
    asyncio.run(create_test_archives())
