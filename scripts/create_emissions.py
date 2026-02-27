"""
Script pour peupler la base de données avec des émissions de test
"""

import asyncio
from datetime import datetime, timedelta
import random

from app.core.database import init_db
from app.models.sport import Sport


# Données de test pour les émissions
EMISSIONS_DATA = [
    {
        "id": "friday_show",
        "title": "FRIDAY SHOW",
        "description": "Le show divertissant du vendredi soir avec des invités exclusifs et des performances en direct",
        "category": "divertissement",
        "subcategory": "show",
        "image": "https://images.unsplash.com/photo-1594381898411-846e7d193883?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1594381898411-846e7d193883?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "duration": 5400,  # 90 minutes
        "date": datetime.now() - timedelta(days=1),
        "presenter": "Michel Bernard",
        "views": 28934,
        "likes": 3456,
        "tags": ["divertissement", "show", "invités", "musique"],
        "featured": True,
        "is_new": False,
    },
    {
        "id": "tele_dici",
        "title": "TÉLÉ D'ICI",
        "description": "Magazine local qui met en valeur les actualités et les personnalités de notre région",
        "category": "magazines",
        "subcategory": "local",
        "image": "https://images.unsplash.com/photo-1573164713988-9665fc5f2f2f?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1573164713988-9665fc5f2f2f?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "duration": 2700,  # 45 minutes
        "date": datetime.now() - timedelta(days=2),
        "presenter": "Marie Dubois",
        "views": 15420,
        "likes": 892,
        "tags": ["local", "actualités", "région", "culture"],
        "featured": False,
        "is_new": False,
    },
    {
        "id": "magazine_culture",
        "title": "MAGAZINE CULTURE",
        "description": "Découverte des tendances culturelles, artistiques et patrimoniales de notre temps",
        "category": "magazines",
        "subcategory": "culture",
        "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "duration": 3600,  # 60 minutes
        "date": datetime.now() - timedelta(days=3),
        "presenter": "Sophie Martin",
        "views": 12456,
        "likes": 1234,
        "tags": ["culture", "art", "patrimoine", "tendances"],
        "featured": True,
        "is_new": False,
    },
    {
        "id": "femmes_dici",
        "title": "FEMMES D'ICI",
        "description": "Portrait de femmes remarquables qui font la différence dans notre société",
        "category": "magazines",
        "subcategory": "société",
        "image": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
        "duration": 2700,  # 45 minutes
        "date": datetime.now() - timedelta(days=4),
        "presenter": "Claire Robert",
        "views": 18934,
        "likes": 2345,
        "tags": ["femmes", "société", "portraits", "engagement"],
        "featured": False,
        "is_new": True,
    },
    {
        "id": "journal_20h",
        "title": "JOURNAL DE 20H",
        "description": "Le journal télévisé complet avec toutes les actualités nationales et internationales",
        "category": "jt",
        "subcategory": "information",
        "image": "https://images.unsplash.com/photo-1495020689064-9584e3bf00e0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1495020689064-9584e3bf00e0?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
        "duration": 1800,  # 30 minutes
        "date": datetime.now() - timedelta(hours=6),
        "presenter": "Jean Dupont",
        "views": 45678,
        "likes": 5678,
        "tags": ["actualités", "information", "politique", "économie"],
        "featured": True,
        "is_new": False,
    },
    {
        "id": "magazine_sante",
        "title": "MAGAZINE SANTÉ",
        "description": "Toutes les actualités santé, bien-être et médecine pour prendre soin de vous",
        "category": "magazines",
        "subcategory": "santé",
        "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
        "duration": 2400,  # 40 minutes
        "date": datetime.now() - timedelta(days=5),
        "presenter": "Dr. Marie Martin",
        "views": 8932,
        "likes": 567,
        "tags": ["santé", "médecine", "bien-être", "prévention"],
        "featured": False,
        "is_new": False,
    },
    {
        "id": "economie_mag",
        "title": "ÉCONOMIE MAG",
        "description": "Magazine dédié à l'actualité économique et financière avec des analyses d'experts",
        "category": "magazines",
        "subcategory": "économie",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
        "duration": 3000,  # 50 minutes
        "date": datetime.now() - timedelta(days=6),
        "presenter": "Pierre Durand",
        "views": 6789,
        "likes": 432,
        "tags": ["économie", "finance", "business", "analyse"],
        "featured": False,
        "is_new": False,
    },
    {
        "id": "doc_histoire",
        "title": "DOCUMENTAIRE HISTOIRE",
        "description": "Plongez dans les coulisses de l'histoire avec des documentaires exclusifs",
        "category": "documentaires",
        "subcategory": "histoire",
        "image": "https://images.unsplash.com/photo-1589998059171-988d887df646?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1589998059171-988d887df646?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        "duration": 4800,  # 80 minutes
        "date": datetime.now() - timedelta(days=7),
        "presenter": "Prof. Robert Dubois",
        "views": 12456,
        "likes": 1234,
        "tags": ["histoire", "documentaire", "culture", "éducation"],
        "featured": True,
        "is_new": False,
    },
    {
        "id": "match_football",
        "title": "MATCH FOOTBALL",
        "description": "Les meilleurs matchs de football avec analyses et commentaires d'experts",
        "category": "sport",
        "subcategory": "football",
        "image": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1517466787929-bc90951d0974?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        "duration": 7200,  # 120 minutes
        "date": datetime.now() - timedelta(days=8),
        "presenter": "Sport Team",
        "views": 45678,
        "likes": 5678,
        "tags": ["sport", "football", "match", "compétition"],
        "featured": False,
        "is_new": False,
    },
    {
        "id": "magazine_nature",
        "title": "MAGAZINE NATURE",
        "description": "Découvrez les merveilles de la nature et de l'environnement",
        "category": "documentaires",
        "subcategory": "nature",
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
        "thumbnail": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?ixlib=rb-1.2.1&auto=format&fit=crop&w=400&q=80",
        "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
        "duration": 3600,  # 60 minutes
        "date": datetime.now() - timedelta(days=9),
        "presenter": "Dr. Alice Nature",
        "views": 9876,
        "likes": 876,
        "tags": ["nature", "environnement", "animaux", "écologie"],
        "featured": False,
        "is_new": True,
    },
]


async def create_test_emissions():
    """Crée les émissions de test dans la base de données MongoDB"""
    
    # Initialiser la base de données
    await init_db()
    
    try:
        # Vérifier si des émissions existent déjà
        existing_count = await Emission.count()
        if existing_count > 0:
            print(f"✅ {existing_count} émissions existent déjà dans la base de données")
            return
        
        # Créer les émissions de test
        created_count = 0
        for emission_data in EMISSIONS_DATA:
            emission = Emission(**emission_data)
            await emission.save()
            created_count += 1
        
        print(f"✅ {created_count} émissions de test créées avec succès")
        
        # Afficher les statistiques
        total_emissions = await Emission.count()
        
        # Compter par catégorie avec agrégation
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        categories = await Emission.aggregate(pipeline).to_list()
        
        print(f"\n📊 Statistiques:")
        print(f"   Total: {total_emissions} émissions")
        for item in categories:
            category = item['_id']
            count = item['count']
            print(f"   {category}: {count} émissions")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des émissions: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Création des émissions de test...")
    asyncio.run(create_test_emissions())
    print("✅ Terminé!")
