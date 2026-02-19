"""
Script de peuplement complet de la base de données BF1 TV
Génère des données de test pour tous les modèles
Usage: python seed.py
"""
import asyncio
from datetime import datetime, timedelta
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.user import User
from app.models.show import Show
from app.models.movie import Movie
from app.models.breakingNews import BreakingNews
from app.models.divertissement import Divertissement
from app.models.popularPrograms import PopularPrograms
from app.models.reel import Reel
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.comment import Comment
from app.models.like import Like
from app.models.favorite import Favorite
from app.models.share import Share
from app.models.program import Program, LiveChannel, ProgramReminder
from app.models.notification import Notification
from app.models.subscription_plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.archive import Archive
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# Charger les variables d'environnement
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_db():
    """Initialiser la connexion à la base de données"""
    MONGODB_URL = os.getenv("MONGODB_URI", "mongodb+srv://bakorobert2000:1jHcf2qX4D53KHyw@cluster0.hfr2vqx.mongodb.net/Bf1_db?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = os.getenv("MONGODB_DBNAME", "Bf1_db")

    print(f"🔌 Connexion à MongoDB: {MONGODB_URL[:50]}...")
    print(f"📦 Base de données: {DATABASE_NAME}\n")

    client = AsyncIOMotorClient(MONGODB_URL)

    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            User, Show, Movie, BreakingNews, Comment, Like, Favorite, Share,
            Divertissement, PopularPrograms, Reel, Reportage, JTandMag,
            Program, LiveChannel, ProgramReminder, Notification,
            SubscriptionPlan, Subscription, Archive
        ]
    )

    print("✅ Connexion à la base de données établie\n")

async def clear_database():
    """Nettoyer toutes les collections"""
    print("🧹 Nettoyage de la base de données...")

    collections = [
        User, Show, Movie, BreakingNews, Comment, Like, Favorite, Share,
        Divertissement, PopularPrograms, Reel, Reportage, JTandMag,
        Program, LiveChannel, ProgramReminder, Notification,
        SubscriptionPlan, Subscription, Archive
    ]

    for collection in collections:
        await collection.delete_all()
        print(f"   ✓ {collection.__name__} vidée")

    print("✅ Base de données nettoyée\n")

async def seed_users():
    """Créer des utilisateurs de test"""
    print("👥 Création des utilisateurs...")

    users_data = [
        {
            "username": "admin",
            "email": "admin@bf1.com",
            "hashed_password": pwd_context.hash("admin123"),
            "is_admin": True,
            "is_premium": True,
            "is_active": True
        },
        {
            "username": "user1",
            "email": "user1@bf1.com",
            "hashed_password": pwd_context.hash("user123"),
            "is_admin": False,
            "is_premium": True,
            "is_active": True
        },
        {
            "username": "user2",
            "email": "user2@bf1.com",
            "hashed_password": pwd_context.hash("user123"),
            "is_admin": False,
            "is_premium": False,
            "is_active": True
        }
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        await user.insert()
        users.append(user)
        print(f"   ✓ {user.username} créé")

    print(f"✅ {len(users)} utilisateurs créés\n")
    return users

async def seed_breaking_news():
    """Créer des actualités"""
    print("📰 Création des actualités...")

    news_data = [
        {
            "title": "Nouvelle loi sur l'éducation adoptée",
            "category": "Politique",
            "description": "Le parlement a adopté une nouvelle loi visant à réformer le système éducatif national.",
            "image": "https://picsum.photos/seed/news1/800/450",
            "author": "Marie Diallo",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "title": "Croissance économique de 5% au dernier trimestre",
            "category": "Économie",
            "description": "Les chiffres officiels montrent une forte reprise de l'activité économique.",
            "image": "https://picsum.photos/seed/news2/800/450",
            "author": "Jean Kouassi",
            "created_at": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "title": "Victoire historique de l'équipe nationale",
            "category": "Sport",
            "description": "L'équipe nationale remporte son premier titre continental après une finale épique.",
            "image": "https://picsum.photos/seed/news3/800/450",
            "author": "Fatou Sow",
            "created_at": datetime.utcnow() - timedelta(hours=8)
        },
        {
            "title": "Inauguration du nouveau centre culturel",
            "category": "Culture",
            "description": "Un nouveau centre culturel ultramoderne ouvre ses portes au public.",
            "image": "https://picsum.photos/seed/news4/800/450",
            "author": "Amadou Traoré",
            "created_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "title": "Sommet international sur le climat",
            "category": "International",
            "description": "Les dirigeants mondiaux se réunissent pour discuter des enjeux climatiques.",
            "image": "https://picsum.photos/seed/news5/800/450",
            "author": "Ibrahim Kone",
            "created_at": datetime.utcnow() - timedelta(days=2)
        }
    ]

    news_list = []
    for news_item in news_data:
        news = BreakingNews(**news_item)
        await news.insert()
        news_list.append(news)
        print(f"   ✓ {news.title}")

    print(f"✅ {len(news_list)} actualités créées\n")
    return news_list

async def seed_live_channels():
    """Créer des chaînes live"""
    print("📺 Création des chaînes live...")

    channels_data = [
        {
            "name": "BF1 TV",
            "channel_number": 1,
            "logo_url": "https://images.unsplash.com/photo-1522869635100-9f4c5e86aa37?w=200",
            "stream_url": "https://example.com/stream/bf1",
            "is_active": True
        },
        {
            "name": "BF1 News",
            "channel_number": 2,
            "logo_url": "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=200",
            "stream_url": "https://example.com/stream/bf1-news",
            "is_active": True
        }
    ]

    channels = []
    for channel_data in channels_data:
        channel = LiveChannel(**channel_data)
        await channel.insert()
        channels.append(channel)
        print(f"   ✓ {channel.name}")

    print(f"✅ {len(channels)} chaînes créées\n")
    return channels

async def seed_programs(channels):
    """Créer des programmes EPG"""
    print("📅 Création des programmes EPG...")

    if not channels:
        print("⚠️  Aucune chaîne disponible, création de programmes ignorée\n")
        return []

    channel = channels[0]
    programs = []

    for day in range(7):
        base_date = datetime.utcnow() + timedelta(days=day)

        programs.append({
            "channel_id": str(channel.id),
            "title": "Journal du Matin",
            "description": "Toute l'actualité du jour avec nos journalistes",
            "type": "Actualités",
            "category": "Journal",
            "start_time": base_date.replace(hour=7, minute=0, second=0),
            "end_time": base_date.replace(hour=8, minute=0, second=0),
            "image_url": "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=400",
            "host": "Marie Diallo"
        })

        programs.append({
            "channel_id": str(channel.id),
            "title": "Le 13H",
            "description": "Journal télévisé de la mi-journée",
            "type": "Actualités",
            "category": "Journal",
            "start_time": base_date.replace(hour=13, minute=0, second=0),
            "end_time": base_date.replace(hour=13, minute=30, second=0),
            "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400",
            "host": "Jean Kouassi"
        })

        programs.append({
            "channel_id": str(channel.id),
            "title": "Le 20H",
            "description": "Journal télévisé du soir",
            "type": "Actualités",
            "category": "Journal",
            "start_time": base_date.replace(hour=20, minute=0, second=0),
            "end_time": base_date.replace(hour=20, minute=45, second=0),
            "image_url": "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=400",
            "host": "Fatou Sow"
        })

    program_list = []
    for prog_data in programs:
        program = Program(**prog_data)
        await program.insert()
        program_list.append(program)

    print(f"   ✓ {len(program_list)} programmes créés")
    print(f"✅ Programmes EPG créés\n")
    return program_list

async def seed_shows():
    """Créer des émissions"""
    print("🎬 Création des émissions...")

    shows_data = [
        {
            "title": "Le Grand Débat",
            "description": "Débat politique hebdomadaire avec les personnalités du moment",
            "category": "Débat",
            "image_url": "https://images.unsplash.com/photo-1590650153855-d9e808231d41?w=800",
            "is_live": True,
            "live_url": "https://example.com/live/grand-debat",
            "host": "Amadou Traoré",
            "duration": "01:30:00",
            "views_count": 0
        },
        {
            "title": "Culture & Vous",
            "description": "Magazine culturel présentant les artistes et événements culturels",
            "category": "Culture",
            "image_url": "https://images.unsplash.com/photo-1514306191717-452ec28c7814?w=800",
            "is_live": False,
            "replay_url": "https://example.com/replay/culture-vous",
            "host": "Aïcha Bah",
            "duration": "00:45:00",
            "views_count": 0
        },
        {
            "title": "Sport Hebdo",
            "description": "Résumé et analyses de l'actualité sportive de la semaine",
            "category": "Sport",
            "image_url": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800",
            "is_live": False,
            "replay_url": "https://example.com/replay/sport-hebdo",
            "host": "Moussa Diop",
            "duration": "01:00:00",
            "views_count": 0
        }
    ]

    shows = []
    for show_data in shows_data:
        show = Show(**show_data)
        await show.insert()
        shows.append(show)
        print(f"   ✓ {show.title}")

    print(f"✅ {len(shows)} émissions créées\n")
    return shows

async def seed_trending_shows():
    """Créer des émissions tendances"""
    print("🔥 Création des émissions tendances...")

    trending_data = [
        {
            "title": "Cuisine du Monde",
            "category": "Cuisine",
            "image": "https://picsum.photos/seed/trending1/800/450",
            "description": "Découvrez les saveurs du monde avec nos chefs",
            "host": "Chef Mamadou",
            "episodes": 24,
            "views": 0,
            "rating": 0
        },
        {
            "title": "Tech & Innovation",
            "category": "Technologie",
            "image": "https://picsum.photos/seed/trending2/800/450",
            "description": "Les dernières innovations technologiques",
            "host": "Sarah Tech",
            "episodes": 18,
            "views": 0,
            "rating": 0
        },
        {
            "title": "Voyage & Découverte",
            "category": "Voyage",
            "image": "https://picsum.photos/seed/trending3/800/450",
            "description": "Explorez les plus beaux endroits du continent",
            "host": "Ibrahim Sall",
            "episodes": 30,
            "views": 0,
            "rating": 0
        },
        {
            "title": "Santé & Bien-être",
            "category": "Santé",
            "image": "https://picsum.photos/seed/trending4/800/450",
            "description": "Conseils santé et bien-être au quotidien",
            "host": "Dr. Aminata",
            "episodes": 20,
            "views": 0,
            "rating": 0
        }
    ]

    trending = []
    for trend_data in trending_data:
        trend = JTandMag(**trend_data)
        await trend.insert()
        trending.append(trend)
        print(f"   ✓ {trend.title}")

    print(f"✅ {len(trending)} émissions tendances créées\n")
    return trending

async def seed_popular_programs():
    """Créer des programmes populaires"""
    print("⭐ Création des programmes populaires...")

    programs_data = [
        {
            "title": "Les Matinales",
            "schedule": "Lun-Ven 07:00",
            "image": "https://picsum.photos/seed/popular1/800/450",
            "description": "Réveillez-vous avec l'actualité du jour",
            "episodes": 250,
            "rating": 0,
            "category": "Actualités"
        },
        {
            "title": "Ciné Club",
            "schedule": "Sam 21:00",
            "image": "https://picsum.photos/seed/popular2/800/450",
            "description": "Les meilleurs films du cinéma africain",
            "episodes": 52,
            "rating": 0,
            "category": "Cinéma"
        },
        {
            "title": "Questions d'Actualité",
            "schedule": "Dim 19:00",
            "image": "https://picsum.photos/seed/popular3/800/450",
            "description": "Débat sur les sujets qui font l'actualité",
            "episodes": 48,
            "rating": 0,
            "category": "Débat"
        },
        {
            "title": "Musique & Rythmes",
            "schedule": "Ven 22:00",
            "image": "https://picsum.photos/seed/popular4/800/450",
            "description": "Découvrez les artistes musicaux du moment",
            "episodes": 40,
            "rating": 0,
            "category": "Musique"
        }
    ]

    programs = []
    for prog_data in programs_data:
        program = PopularPrograms(**prog_data)
        await program.insert()
        programs.append(program)
        print(f"   ✓ {program.title}")

    print(f"✅ {len(programs)} programmes populaires créés\n")
    return programs

async def seed_reportages():
    """Créer des reportages"""
    print("📹 Création des reportages...")

    reportages_data = [
        {
            "title": "Journal du 20H - 05/02/2026",
            "description": "Replay du journal télévisé du soir",
            "category": "Actualités",
            "thumbnail": "https://picsum.photos/seed/replay1/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "duration_minutes": 45,
            "views": 0,
            "rating": 4.5,
            "aired_at": datetime.utcnow() - timedelta(days=1),
            "program_title": "Le 20H",
            "host": "Fatou Sow"
        },
        {
            "title": "Le Grand Débat - Épisode 12",
            "description": "Débat sur la réforme de l'éducation",
            "category": "Débat",
            "thumbnail": "https://picsum.photos/seed/replay2/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "duration_minutes": 90,
            "views": 0,
            "rating": 4.7,
            "aired_at": datetime.utcnow() - timedelta(days=2),
            "program_title": "Le Grand Débat",
            "host": "Amadou Traoré"
        },
        {
            "title": "Sport Hebdo - Résumé",
            "description": "Tous les temps forts sportifs de la semaine",
            "category": "Sport",
            "thumbnail": "https://picsum.photos/seed/replay3/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "duration_minutes": 60,
            "views": 0,
            "rating": 4.3,
            "aired_at": datetime.utcnow() - timedelta(days=3),
            "program_title": "Sport Hebdo",
            "host": "Moussa Diop"
        },
        {
            "title": "Culture & Vous - Spécial Musique",
            "description": "Rencontre avec les artistes musicaux",
            "category": "Culture",
            "thumbnail": "https://picsum.photos/seed/replay4/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "duration_minutes": 45,
            "views": 0,
            "rating": 4.6,
            "aired_at": datetime.utcnow() - timedelta(days=4),
            "program_title": "Culture & Vous",
            "host": "Aïcha Bah"
        }
    ]

    reportages = []
    for reportage_data in reportages_data:
        reportage = Reportage(**reportage_data)
        await reportage.insert()
        reportages.append(reportage)
        print(f"   ✓ {reportage.title}")

    print(f"✅ {len(reportages)} reportages créés\n")
    return reportages

async def seed_movies():
    """Créer des films"""
    print("🎥 Création des films...")

    movies_data = [
        {
            "title": "Le Destin de Koumba",
            "description": "Un drame poignant sur une jeune femme qui lutte pour ses rêves",
            "genre": ["Drame", "Romance"],
            "duration": 135,
            "release_date": datetime(2024, 6, 15),
            "image_url": "https://picsum.photos/seed/movie1/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "is_premium": True
        },
        {
            "title": "Les Gardiens de la Savane",
            "description": "Une aventure épique dans les terres sauvages d'Afrique",
            "genre": ["Aventure", "Action"],
            "duration": 115,
            "release_date": datetime(2025, 3, 20),
            "image_url": "https://picsum.photos/seed/movie2/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
            "is_premium": False
        },
        {
            "title": "Rires et Larmes",
            "description": "Une comédie familiale touchante et hilarante",
            "genre": ["Comédie", "Famille"],
            "duration": 100,
            "release_date": datetime(2025, 1, 10),
            "image_url": "https://picsum.photos/seed/movie3/800/450",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "is_premium": False
        }
    ]

    movies = []
    for movie_data in movies_data:
        movie = Movie(**movie_data)
        await movie.insert()
        movies.append(movie)
        print(f"   ✓ {movie.title}")

    print(f"✅ {len(movies)} films créés\n")
    return movies

async def seed_reels():
    """Créer des reels"""
    print("📱 Création des reels...")

    reels_data = [
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4",
            "title": "Coulisses du JT",
            "username": "BF1_Official",
            "description": "Découvrez les coulisses de notre journal télévisé",
            "likes": 0,
            "comments": 0,
            "shares": 0
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
            "title": "Moment drôle en direct",
            "username": "BF1_Bloopers",
            "description": "Les moments les plus drôles de nos émissions",
            "likes": 0,
            "comments": 0,
            "shares": 0
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
            "title": "Interview express",
            "username": "BF1_News",
            "description": "Interview rapide avec le ministre de la culture",
            "likes": 0,
            "comments": 0,
            "shares": 0
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
            "title": "Résumé sportif",
            "username": "BF1_Sport",
            "description": "Les meilleurs moments du match d'hier",
            "likes": 0,
            "comments": 0,
            "shares": 0
        }
    ]

    reels = []
    for reel_data in reels_data:
        reel = Reel(**reel_data)
        await reel.insert()
        reels.append(reel)
        print(f"   ✓ {reel.title}")

    print(f"✅ {len(reels)} reels créés\n")
    return reels

async def seed_interviews():
    """Créer des interviews"""
    print("🎤 Création des interviews...")

    interviews_data = [
        {
            "title": "Interview avec le Ministre de l'Éducation",
            "guest_name": "Dr. Mamadou Diallo",
            "guest_role": "Ministre de l'Éducation Nationale",
            "description": "Discussion sur la réforme du système éducatif",
            "image": "https://picsum.photos/seed/interview1/800/450",
            "duration_minutes": 35,
            "published_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "title": "Rencontre avec l'artiste Youssou N'Dour",
            "guest_name": "Youssou N'Dour",
            "guest_role": "Artiste et Musicien",
            "description": "Parcours et projets du célèbre artiste sénégalais",
            "image": "https://picsum.photos/seed/interview2/800/450",
            "duration_minutes": 45,
            "published_at": datetime.utcnow() - timedelta(days=3)
        }
    ]

    interviews = []
    for interview_data in interviews_data:
        interview = Interview(**interview_data)
        await interview.insert()
        interviews.append(interview)
        print(f"   ✓ {interview.title}")

    print(f"✅ {len(interviews)} interviews créées\n")
    return interviews

async def seed_archives():
    """Créer des archives vidéo premium"""
    print("📹 Création des archives vidéo...")
    
    now = datetime.utcnow()
    archives_data = [
        {
            "title": "Interview exclusive: Le Président face aux citoyens",
            "guest_name": "Emmanuel Président",
            "guest_role": "Président de la République",
            "description": "Une interview historique où le Président répond aux questions des citoyens sur la politique économique et sociale.",
            "duration_minutes": 65,
            "is_premium": True,
            "price": 3500,
            "category": "Politique",
            "tags": ["politique", "président", "économie"],
            "archived_date": now - timedelta(days=45),
            "views": 3500,
            "rating": 4.7,
            "rating_count": 142,
            "purchases_count": 89,
            "popularity_score": 1050.0 + 665.4 + 17.8,
            "image": "https://picsum.photos/seed/archive1/800/450",
            "thumbnail": "https://picsum.photos/seed/archive1_thumb/400/225",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        },
        {
            "title": "Débat: L'avenir de l'éducation nationale",
            "guest_name": "Sophie Éducation",
            "guest_role": "Ministre de l'Éducation",
            "description": "Un débat approfondi sur les réformes de l'éducation et le numérique à l'école.",
            "duration_minutes": 52,
            "is_premium": True,
            "price": 3000,
            "category": "Éducation",
            "tags": ["éducation", "réforme", "école"],
            "archived_date": now - timedelta(days=30),
            "views": 2100,
            "rating": 4.3,
            "rating_count": 87,
            "purchases_count": 56,
            "popularity_score": 630.0 + 187.05 + 11.2,
            "image": "https://picsum.photos/seed/archive2/800/450",
            "thumbnail": "https://picsum.photos/seed/archive2_thumb/400/225",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        },
        {
            "title": "Crise sanitaire: Retour sur la pandémie",
            "guest_name": "Dr. Pierre Santé",
            "guest_role": "Directeur Général de la Santé",
            "description": "Analyse complète de la gestion de la crise sanitaire et perspectives pour l'avenir.",
            "duration_minutes": 58,
            "is_premium": True,
            "price": 2500,
            "category": "Santé",
            "tags": ["santé", "covid", "pandémie"],
            "archived_date": now - timedelta(days=20),
            "views": 4200,
            "rating": 4.8,
            "rating_count": 201,
            "purchases_count": 134,
            "popularity_score": 1260.0 + 482.4 + 26.8,
            "image": "https://picsum.photos/seed/archive3/800/450",
            "thumbnail": "https://picsum.photos/seed/archive3_thumb/400/225",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
        },
        {
            "title": "Révolution technologique: IA et société",
            "guest_name": "Marc Innovation",
            "guest_role": "CEO TechCorp France",
            "description": "Discussion sur l'intelligence artificielle et son impact sur nos vies.",
            "duration_minutes": 48,
            "is_premium": False,
            "price": 0,
            "category": "Technologie",
            "tags": ["technologie", "IA", "innovation"],
            "archived_date": now - timedelta(days=15),
            "views": 5800,
            "rating": 4.9,
            "rating_count": 287,
            "purchases_count": 0,
            "popularity_score": 1740.0 + 703.15 + 0.0,
            "image": "https://picsum.photos/seed/archive4/800/450",
            "thumbnail": "https://picsum.photos/seed/archive4_thumb/400/225",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
        },
        {
            "title": "Patrimoine culturel français",
            "guest_name": "Isabelle Culture",
            "guest_role": "Conservatrice du Musée National",
            "description": "Exploration du patrimoine culturel français et son importance pour notre identité.",
            "duration_minutes": 55,
            "is_premium": True,
            "price": 2800,
            "category": "Culture",
            "tags": ["culture", "patrimoine", "histoire"],
            "archived_date": now - timedelta(days=10),
            "views": 1850,
            "rating": 4.5,
            "rating_count": 76,
            "purchases_count": 48,
            "popularity_score": 555.0 + 171.0 + 9.6,
            "image": "https://picsum.photos/seed/archive5/800/450",
            "thumbnail": "https://picsum.photos/seed/archive5_thumb/400/225",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
        },
    ]
    
    archives = []
    for archive_data in archives_data:
        archive = Archive(**archive_data)
        await archive.insert()
        archives.append(archive)
        premium = "🔒 Premium" if archive.is_premium else "🆓 Gratuit"
        price_display = f"{int(archive.price)} XOF" if archive.price > 0 else "Gratuit"
        print(f"   ✓ {archive.title} {premium} ({price_display})")
    
    print(f"✅ {len(archives)} archives créées\n")
    return archives

async def seed_subscription_plans():
    """Créer des plans d'abonnement"""
    print("💳 Création des plans d'abonnement...")

    plans_data = [
        {
            "code": "free",
            "name": "Gratuit",
            "duration_months": 1,
            "price_cents": 0,
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "monthly",
            "name": "Premium Mensuel",
            "duration_months": 1,
            "price_cents": 250000,
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "quarterly",
            "name": "Premium Trimestriel",
            "duration_months": 3,
            "price_cents": 700000,
            "currency": "XOF",
            "is_active": True
        },
        {
            "code": "yearly",
            "name": "Premium Annuel",
            "duration_months": 12,
            "price_cents": 2500000,
            "currency": "XOF",
            "is_active": True
        }
    ]

    plans = []
    for plan_data in plans_data:
        plan = SubscriptionPlan(**plan_data)
        await plan.insert()
        plans.append(plan)
        print(f"   ✓ {plan.name} - {plan.price_cents} {plan.currency}")

    print(f"✅ {len(plans)} plans d'abonnement créés\n")
    return plans

async def main():
    """Fonction principale"""
    try:
        await init_db()

        print("⚠️  ATTENTION: Nettoyage et recréation de toutes les données...")
        print()
        await clear_database()

        users = await seed_users()
        news = await seed_breaking_news()
        channels = await seed_live_channels()
        programs = await seed_programs(channels)
        shows = await seed_shows()
        trending = await seed_trending_shows()
        popular = await seed_popular_programs()
        replays = await seed_replays()
        movies = await seed_movies()
        reels = await seed_reels()
        interviews = await seed_interviews()
        archives = await seed_archives()
        plans = await seed_subscription_plans()

        print("=" * 60)
        print("✅ PEUPLEMENT TERMINÉ AVEC SUCCÈS!")
        print("=" * 60)
        print("\n📊 Résumé:")
        print(f"   • {len(users)} utilisateurs")
        print(f"   • {len(news)} actualités")
        print(f"   • {len(channels)} chaînes live")
        print(f"   • {len(programs)} programmes EPG")
        print(f"   • {len(shows)} émissions")
        print(f"   • {len(trending)} émissions tendances")
        print(f"   • {len(popular)} programmes populaires")
        print(f"   • {len(replays)} replays")
        print(f"   • {len(movies)} films")
        print(f"   • {len(reels)} reels")
        print(f"   • {len(interviews)} interviews")
        print(f"   • {len(archives)} archives vidéo premium")
        print(f"   • {len(plans)} plans d'abonnement")
        print("\n🔑 Comptes de test:")
        print("   • Admin: admin@bf1.com / admin123")
        print("   • User Premium: user1@bf1.com / user123")
        print("   • User Gratuit: user2@bf1.com / user123")

    except Exception as e:
        print(f"\n❌ Erreur lors du peuplement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 SCRIPT DE PEUPLEMENT BF1 TV")
    print("=" * 60)
    print()
    asyncio.run(main())
    print("\n" + "=" * 60)
