"""
Script pour peupler la base de données avec des données de test pour BF1 TV
"""
from datetime import datetime, timedelta
from app.models.user import User
from app.models.show import Show
from app.models.movie import Movie
from app.models.news import News
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
            "video_url": "https://stream.bf1tv.com/movies/dernier-voyage",
            "is_premium": False,
        },
        {
            "title": "Amour à Paris",
            "description": "Une histoire d'amour romantique dans les rues de Paris",
            "duration": 105,
            "genre": ["Romance", "Comédie"],
            "image_url": "https://picsum.photos/seed/romance1/600/900",
            "video_url": "https://stream.bf1tv.com/movies/amour-paris",
            "is_premium": True,
        },
        {
            "title": "Mission Impossible: Retour",
            "description": "Action et espionnage au plus haut niveau",
            "duration": 135,
            "genre": ["Action", "Espionnage"],
            "image_url": "https://picsum.photos/seed/action1/600/900",
            "video_url": "https://stream.bf1tv.com/movies/mission-retour",
            "is_premium": True,
        },
        {
            "title": "Documentaire Nature",
            "description": "Exploration de la faune sauvage africaine",
            "duration": 85,
            "genre": ["Documentaire", "Nature"],
            "image_url": "https://picsum.photos/seed/nature1/600/900",
            "video_url": "https://stream.bf1tv.com/movies/doc-nature",
            "is_premium": False,
        },
        {
            "title": "Comédie Familiale",
            "description": "Un film drôle pour toute la famille",
            "duration": 95,
            "genre": ["Comédie", "Famille"],
            "image_url": "https://picsum.photos/seed/comedie1/600/900",
            "video_url": "https://stream.bf1tv.com/movies/comedie-familiale",
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
            "duration": 30,
            "category": "Actualités",
            "edition": "19H30",
            "start_time": now.replace(hour=19, minute=30, second=0),
            "end_time": now.replace(hour=20, minute=0, second=0),
            "image_url": "https://picsum.photos/seed/jt1930/800/450",
            "is_live": True,
            "live_url": "https://stream.bf1tv.com/live/jt1930",
            "replay_url": "https://replay.bf1tv.com/videos/jt1930",
            "is_featured": True,
            "tags": ["actualités", "direct", "journal"],
        },
        {
            "title": "Journal Télévisé 13h30",
            "description": "Le journal de la mi-journée",
            "host": "Pierre Martin",
            "duration": 30,
            "category": "Actualités",
            "edition": "13H30",
            "start_time": now.replace(hour=13, minute=30, second=0),
            "end_time": now.replace(hour=14, minute=0, second=0),
            "image_url": "https://picsum.photos/seed/jt1330/800/450",
            "is_live": False,
            "live_url": "https://stream.bf1tv.com/live/jt1330",
            "replay_url": "https://replay.bf1tv.com/videos/jt1330",
            "is_featured": False,
            "tags": ["actualités", "journal"],
        },
        {
            "title": "Sport en Direct",
            "description": "Toute l'actualité sportive du jour",
            "host": "Jean Dupont",
            "duration": 60,
            "category": "Sport",
            "start_time": now.replace(hour=20, minute=30, second=0),
            "end_time": now.replace(hour=21, minute=30, second=0),
            "image_url": "https://picsum.photos/seed/sport/800/450",
            "is_live": True,
            "live_url": "https://stream.bf1tv.com/live/sport",
            "replay_url": "https://replay.bf1tv.com/videos/sport-direct",
            "is_featured": True,
            "tags": ["sport", "direct", "football"],
        },
        {
            "title": "Divertissement du Soir",
            "description": "Émission de divertissement avec invités",
            "host": "Marc Leblanc",
            "duration": 90,
            "category": "Divertissement",
            "start_time": now + timedelta(days=2, hours=21),
            "end_time": now + timedelta(days=2, hours=22, minutes=30),
            "image_url": "https://picsum.photos/seed/divertissement/800/450",
            "is_live": False,
            "live_url": "https://stream.bf1tv.com/live/divertissement",
            "replay_url": "https://replay.bf1tv.com/videos/divertissement-soir",
            "is_featured": True,
            "tags": ["divertissement", "humour", "talk-show"],
        },
        {
            "title": "Culture & Vous",
            "description": "Magazine culturel hebdomadaire",
            "host": "Sophie Laurent",
            "duration": 45,
            "category": "Culture",
            "start_time": now + timedelta(days=1, hours=20),
            "end_time": now + timedelta(days=1, hours=20, minutes=45),
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


async def seed_news():
    """Créer des actualités de test"""
    now = datetime.utcnow()
    
    news_data = [
        {
            "title": "Nouvelle loi sur l'environnement adoptée",
            "content": "Le parlement a voté aujourd'hui une nouvelle loi visant à réduire les émissions de CO2 de 40% d'ici 2030.",
            "author": "Marie Dubois",
            "category": "Politique",
            "edition": "19H30",
            "image_url": "https://picsum.photos/seed/news1/800/450",
            "is_live": True,
            "live_url": "https://stream.bf1tv.com/news/loi-environnement",
            "published_at": now,
            "tags": ["politique", "environnement", "actualité"],
        },
        {
            "title": "Victoire historique en Coupe du Monde",
            "content": "L'équipe nationale remporte la Coupe du Monde après un match palpitant.",
            "author": "Jean Dupont",
            "category": "Sport",
            "image_url": "https://picsum.photos/seed/news2/800/450",
            "is_live": False,
            "published_at": now - timedelta(hours=2),
            "tags": ["sport", "football", "coupe du monde"],
        },
        {
            "title": "Exposition d'art contemporain au Louvre",
            "content": "Une nouvelle exposition présente les œuvres de 50 artistes contemporains du monde entier.",
            "author": "Sophie Laurent",
            "category": "Culture",
            "image_url": "https://picsum.photos/seed/news3/800/450",
            "is_live": False,
            "published_at": now - timedelta(hours=5),
            "tags": ["culture", "art", "exposition"],
        },
        {
            "title": "Nouvelle technologie révolutionnaire",
            "content": "Des chercheurs annoncent une percée majeure dans le domaine de l'intelligence artificielle.",
            "author": "Pierre Martin",
            "category": "Technologie",
            "edition": "13H30",
            "image_url": "https://picsum.photos/seed/news4/800/450",
            "is_live": False,
            "published_at": now - timedelta(hours=8),
            "tags": ["technologie", "IA", "innovation"],
        },
        {
            "title": "Sommet international sur le climat",
            "content": "Les dirigeants mondiaux se réunissent pour discuter des actions urgentes contre le changement climatique.",
            "author": "Marie Dubois",
            "category": "International",
            "image_url": "https://picsum.photos/seed/news5/800/450",
            "is_live": True,
            "live_url": "https://stream.bf1tv.com/news/sommet-climat",
            "published_at": now - timedelta(minutes=30),
            "tags": ["international", "climat", "politique"],
        },
    ]
    
    created_news = []
    for news_item_data in news_data:
        existing = await News.find_one(News.title == news_item_data["title"])
        if not existing:
            news_item = News(**news_item_data)
            await news_item.insert()
            created_news.append(news_item)
            print(f"✅ Actualité créée: {news_item.title}")
        else:
            print(f"⚠️  Actualité existe déjà: {news_item_data['title']}")
            created_news.append(existing)
    
    return created_news


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
    news = await seed_news()
    print(f"✅ {len(news)} actualités créées/vérifiées\n")
    
    print("🎉 Peuplement terminé avec succès!")
    print(f"\n📊 Résumé:")
    print(f"   - Utilisateurs: {len(users)}")
    print(f"   - Émissions: {len(shows)}")
    print(f"   - Films: {len(movies)}")
    print(f"   - Actualités: {len(news)}")