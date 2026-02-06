"""
Script pour peupler la base de données avec des données de test pour BF1 TV
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from datetime import datetime, timedelta
from app.models.user import User
from app.models.show import Show
from app.models.movie import Movie
from app.models.breakingNews import BreakingNews
from app.models.interview import Interview
from app.models.popularPrograms import PopularPrograms
from app.models.reel import Reel
from app.models.replay import Replay
from app.models.trendingShow import TrendingShow
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_users():
    """Créer des utilisateurs de test"""
    users_data = [
        {
            "username": "admin",
            "email": "admin@bf1tv.com",
            "hashed_password": pwd_context.hash("admin123"),
            "is_admin": True,
            "is_premium": True,
        },
        {
            "username": "user1",
            "email": "user1@bf1tv.com",
            "hashed_password": pwd_context.hash("user123"),
            "is_admin": False,
            "is_premium": False,
        },
        {
            "username": "premium_user",
            "email": "premium@bf1tv.com",
            "hashed_password": pwd_context.hash("premium123"),
            "is_admin": False,
            "is_premium": True,
        },
    ]
    
    created_users = []
    for user_data in users_data:
        existing = await User.find_one(User.email == user_data["email"])
        if not existing:
            user = User(**user_data)
            await user.insert()
            created_users.append(user)
            print(f"✅ Utilisateur créé: {user.username}")
        else:
            print(f"⚠️  Utilisateur existe déjà: {user_data['username']}")
            created_users.append(existing)
    
    return created_users


async def seed_movies():
    """Créer des films de test"""
    movies_data = [
        {
            "title": "Le Dernier Voyage",
            "description": "Un thriller captivant sur un voyage qui tourne mal",
            "duration": 120,
            "genre": ["Thriller", "Suspense"],
            "image_url": "https://picsum.photos/seed/thriller1/600/900",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "is_premium": False,
        },
        {
            "title": "Amour à Paris",
            "description": "Une histoire d'amour romantique dans les rues de Paris",
            "duration": 105,
            "genre": ["Romance", "Comédie"],
            "image_url": "https://picsum.photos/seed/romance1/600/900",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "is_premium": True,
        },
        {
            "title": "Mission Impossible: Retour",
            "description": "Action et espionnage au plus haut niveau",
            "duration": 135,
            "genre": ["Action", "Espionnage"],
            "image_url": "https://picsum.photos/seed/action1/600/900",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
            "is_premium": True,
        },
        {
            "title": "Documentaire Nature",
            "description": "Exploration de la faune sauvage africaine",
            "duration": 85,
            "genre": ["Documentaire", "Nature"],
            "image_url": "https://picsum.photos/seed/nature1/600/900",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "is_premium": False,
        },
        {
            "title": "Comédie Familiale",
            "description": "Un film drôle pour toute la famille",
            "duration": 95,
            "genre": ["Comédie", "Famille"],
            "image_url": "https://picsum.photos/seed/comedie1/600/900",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "is_premium": False,
        },
    ]
    
    created_movies = []
    for movie_data in movies_data:
        existing = await Movie.find_one(Movie.title == movie_data["title"])
        if not existing:
            movie = Movie(**movie_data)
            await movie.insert()
            created_movies.append(movie)
            print(f"✅ Film créé: {movie.title}")
        else:
            print(f"⚠️  Film existe déjà: {movie_data['title']}")
            created_movies.append(existing)
    
    return created_movies


async def seed_shows():
    """Créer des émissions de test"""
    now = datetime.utcnow()
    
    shows_data = [
        {
            "title": "Journal Télévisé 19h30",
            "description": "L'actualité nationale et internationale en direct",
            "host": "Marie Dubois",
            "category": "Actualités",
            "image_url": "https://picsum.photos/seed/jt1930/800/450",
            "is_live": True,
            "stream_url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
            "is_featured": True,
            "tags": ["actualités", "direct", "journal"],
        },
        {
            "title": "Journal Télévisé 13h30",
            "description": "Le journal de la mi-journée",
            "host": "Pierre Martin",
            "category": "Actualités",
            "image_url": "https://picsum.photos/seed/jt1330/800/450",
            "is_live": False,
            "is_replay": True,
            "replay_at": now - timedelta(hours=2),
            "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "is_featured": False,
            "tags": ["actualités", "journal"],
        },
        {
            "title": "Sport en Direct",
            "description": "Toute l'actualité sportive du jour",
            "host": "Jean Dupont",
            "category": "Sport",
            "image_url": "https://picsum.photos/seed/sport/800/450",
            "is_live": True,
            "stream_url": "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_4x3/gear1/prog_index.m3u8",
            "is_featured": True,
            "tags": ["sport", "direct", "football"],
        },
        {
            "title": "Divertissement du Soir",
            "description": "Émission de divertissement avec invités",
            "host": "Marc Leblanc",
            "category": "Divertissement",
            "image_url": "https://picsum.photos/seed/divertissement/800/450",
            "is_live": False,
            "is_replay": True,
            "replay_at": now - timedelta(days=1),
            "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "is_featured": True,
            "tags": ["divertissement", "humour", "talk-show"],
        },
        {
            "title": "Culture & Vous",
            "description": "Magazine culturel hebdomadaire",
            "host": "Sophie Laurent",
            "category": "Culture",
            "image_url": "https://picsum.photos/seed/culture/800/450",
            "is_live": False,
            "is_featured": False,
            "tags": ["culture", "magazine", "art"],
        },
    ]
    
    created_shows = []
    for show_data in shows_data:
        existing = await Show.find_one(Show.title == show_data["title"])
        if not existing:
            show = Show(**show_data)
            await show.insert()
            created_shows.append(show)
            print(f"✅ Émission créée: {show.title}")
        else:
            print(f"⚠️  Émission existe déjà: {show_data['title']}")
            created_shows.append(existing)
    
    return created_shows


async def seed_breaking_news():
    """Créer des breaking news de test"""
    news_data = [
        {
            "title": "Nouvelle loi sur l'environnement adoptée",
            "description": "Le parlement a voté une loi visant à réduire les émissions de CO2 de 40% d'ici 2030.",
            "author": "Marie Dubois",
            "category": "Politique",
            "image": "https://picsum.photos/seed/bn1/800/450",
        },
        {
            "title": "Victoire historique en Coupe du Monde",
            "description": "L'équipe nationale remporte la Coupe du Monde après un match palpitant.",
            "author": "Jean Dupont",
            "category": "Sport",
            "image": "https://picsum.photos/seed/bn2/800/450",
        },
        {
            "title": "Exposition d'art contemporain au Louvre",
            "description": "Une nouvelle exposition présente les œuvres de 50 artistes contemporains.",
            "author": "Sophie Laurent",
            "category": "Culture",
            "image": "https://picsum.photos/seed/bn3/800/450",
        },
    ]

    created_news = []
    for news_item_data in news_data:
        existing = await BreakingNews.find_one(BreakingNews.title == news_item_data["title"])
        if not existing:
            news_item = BreakingNews(**news_item_data)
            await news_item.insert()
            created_news.append(news_item)
            print(f"✅ Breaking news créée: {news_item.title}")
        else:
            print(f"⚠️  Breaking news existe déjà: {news_item_data['title']}")
            created_news.append(existing)

    return created_news


async def seed_interviews():
    """Créer des interviews de test"""
    interviews_data = [
        {
            "title": "Entretien avec la ministre de la Santé",
            "guest_name": "Claire Martin",
            "guest_role": "Ministre de la Santé",
            "image": "https://picsum.photos/seed/interview1/800/450",
            "description": "Discussion sur la réforme hospitalière.",
            "duration_minutes": 35,
            "views": 1200,
            "rating": 4.5,
        },
        {
            "title": "Interview d'un chef étoilé",
            "guest_name": "Lucas Bernard",
            "guest_role": "Chef étoilé",
            "image": "https://picsum.photos/seed/interview2/800/450",
            "description": "Cuisine durable et créativité.",
            "duration_minutes": 28,
            "views": 900,
            "rating": 4.2,
        },
    ]

    created = []
    for data in interviews_data:
        existing = await Interview.find_one(Interview.title == data["title"])
        if not existing:
            item = Interview(**data)
            await item.insert()
            created.append(item)
            print(f"✅ Interview créée: {item.title}")
        else:
            print(f"⚠️  Interview existe déjà: {data['title']}")
            created.append(existing)

    return created


async def seed_reels():
    """Créer des reels de test"""
    reels_data = [
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4",
            "title": "Moment fort du match",
            "username": "bf1_sport",
            "description": "Résumé express de l'action clé.",
            "likes": 250,
            "comments": 18,
            "shares": 12,
        },
        {
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
            "title": "Coulisses du tournage",
            "username": "bf1_tv",
            "description": "Découverte des coulisses.",
            "likes": 180,
            "comments": 10,
            "shares": 6,
        },
    ]

    created = []
    for data in reels_data:
        existing = await Reel.find_one(Reel.title == data["title"])
        if not existing:
            item = Reel(**data)
            await item.insert()
            created.append(item)
            print(f"✅ Reel créé: {item.title}")
        else:
            print(f"⚠️  Reel existe déjà: {data['title']}")
            created.append(existing)

    return created


async def seed_replays():
    """Créer des replays de test"""
    now = datetime.utcnow()
    replays_data = [
        {
            "title": "Replay Journal 19h30",
            "category": "Actualités",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "thumbnail": "https://picsum.photos/seed/replay1/800/450",
            "description": "Replay complet du journal du soir.",
            "duration_minutes": 30,
            "program_title": "Journal Télévisé",
            "host": "Marie Dubois",
            "views": 2000,
            "rating": 4.6,
            "aired_at": now - timedelta(days=1),
        },
    ]

    created = []
    for data in replays_data:
        existing = await Replay.find_one(Replay.title == data["title"])
        if not existing:
            item = Replay(**data)
            await item.insert()
            created.append(item)
            print(f"✅ Replay créé: {item.title}")
        else:
            print(f"⚠️  Replay existe déjà: {data['title']}")
            created.append(existing)

    return created


async def seed_popular_programs():
    """Créer des programmes populaires de test"""
    programs_data = [
        {
            "title": "Le Grand Débat",
            "schedule": "Jeudi 21:00",
            "image": "https://picsum.photos/seed/program1/800/450",
            "description": "Débat hebdomadaire sur l'actualité.",
            "episodes": 24,
            "rating": 4.3,
            "category": "Débat",
        },
    ]

    created = []
    for data in programs_data:
        existing = await PopularPrograms.find_one(PopularPrograms.title == data["title"])
        if not existing:
            item = PopularPrograms(**data)
            await item.insert()
            created.append(item)
            print(f"✅ Programme populaire créé: {item.title}")
        else:
            print(f"⚠️  Programme populaire existe déjà: {data['title']}")
            created.append(existing)

    return created


async def seed_trending_shows():
    """Créer des tendances d'émissions de test"""
    shows_data = [
        {
            "title": "Top Talk Show",
            "category": "Talk Show",
            "image": "https://picsum.photos/seed/trending1/800/450",
            "description": "Le talk show le plus regardé.",
            "host": "Nadia Karim",
            "episodes": 52,
            "views": 45000,
            "rating": 4.8,
        },
    ]

    created = []
    for data in shows_data:
        existing = await TrendingShow.find_one(TrendingShow.title == data["title"])
        if not existing:
            item = TrendingShow(**data)
            await item.insert()
            created.append(item)
            print(f"✅ Trending show créé: {item.title}")
        else:
            print(f"⚠️  Trending show existe déjà: {data['title']}")
            created.append(existing)

    return created


async def seed_all():
    """Peupler toute la base de données"""
    print("\n🌱 Début du peuplement de la base de données BF1 TV...\n")
    
    print("👥 Création des utilisateurs...")
    users = await seed_users()
    print(f"✅ {len(users)} utilisateurs créés/vérifiés\n")
    
    print("📺 Création des émissions...")
    shows = await seed_shows()
    print(f"✅ {len(shows)} émissions créées/vérifiées\n")
    
    print("🎬 Création des films...")
    movies = await seed_movies()
    print(f"✅ {len(movies)} films créés/vérifiés\n")
    
    print("📰 Création des actualités...")
    news = await seed_breaking_news()
    print(f"✅ {len(news)} breaking news créées/vérifiées\n")

    print("🎙️ Création des interviews...")
    interviews = await seed_interviews()
    print(f"✅ {len(interviews)} interviews créées/vérifiées\n")

    print("🎞️ Création des reels...")
    reels = await seed_reels()
    print(f"✅ {len(reels)} reels créés/vérifiés\n")

    print("⏯️ Création des replays...")
    replays = await seed_replays()
    print(f"✅ {len(replays)} replays créés/vérifiés\n")

    print("🔥 Création des trending shows...")
    trending = await seed_trending_shows()
    print(f"✅ {len(trending)} trending shows créés/vérifiés\n")

    print("⭐ Création des programmes populaires...")
    programs = await seed_popular_programs()
    print(f"✅ {len(programs)} programmes populaires créés/vérifiés\n")
    
    print("🎉 Peuplement terminé avec succès!")
    print(f"\n📊 Résumé:")
    print(f"   - Utilisateurs: {len(users)}")
    print(f"   - Émissions: {len(shows)}")
    print(f"   - Films: {len(movies)}")
    print(f"   - Breaking news: {len(news)}")
    print(f"   - Interviews: {len(interviews)}")
    print(f"   - Reels: {len(reels)}")
    print(f"   - Replays: {len(replays)}")
    print(f"   - Trending shows: {len(trending)}")
    print(f"   - Programmes populaires: {len(programs)}")