import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, APIRouter
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.config import init_db
from app.config.settings import settings
from app.core.cors import setup_cors
from app.core.error_handlers import setup_error_handlers
from app.core.middlewares import setup_middlewares
from app.core.error_resilience import resilience_middleware
from app.utils.cache import cache_manager
# RateLimitMiddleware retiré pour accepter toutes les requêtes
# from app.utils.rate_limiter import RateLimitMiddleware

from app.api import (
    movies, users, favorites, breakingNews, notifications, subscriptions, payments, premium,
    contact, comments, likes, messages, jtandmag, reel, reportage, divertissement, shares,
    programs, stats, user_settings, support, about, archives, liveStream, upload, views, username_generator,
    websocket, subscription_plans, emission_categories, search, series, carousel,
    tele_realite, section_categories
)
from app.api import sport
from app.core.scheduler import start_scheduler, stop_scheduler


async def _migrate_likes_field():
    """Initialise likes=0 pour les docs sans ce champ, puis resynchronise depuis la collection likes."""
    from app.models.breakingNews import BreakingNews
    from app.models.divertissement import Divertissement
    from app.models.reportage import Reportage
    from app.models.jtandmag import JTandMag
    from app.models.archive import Archive
    from app.models.movie import Movie
    from app.models.tele_realite import TeleRealite
    from app.models.like import Like

    # Etape 1 : initialiser le champ manquant
    model_type_map = {
        "breaking_news": BreakingNews,
        "divertissement": Divertissement,
        "reportage": Reportage,
        "jtandmag": JTandMag,
        "archive": Archive,
        "movie": Movie,
        "tele_realite": TeleRealite,
        "event": TeleRealite,
    }
    for Model in model_type_map.values():
        try:
            col = Model.get_motor_collection()
            await col.update_many({"likes": {"$exists": False}}, {"$set": {"likes": 0}})
        except Exception as e:
            print(f"[Migration] Erreur init {Model.__name__}: {e}")

    # Etape 2 : recalculer le vrai compteur depuis la collection likes
    try:
        pipeline = [
            {"$group": {"_id": {"content_id": "$content_id", "content_type": "$content_type"}, "count": {"$sum": 1}}}
        ]
        like_col = Like.get_motor_collection()
        async for row in like_col.aggregate(pipeline):
            ctype = row["_id"]["content_type"]
            cid   = row["_id"]["content_id"]
            count = row["count"]
            Model = model_type_map.get(ctype)
            if not Model:
                continue
            try:
                from bson import ObjectId
                col = Model.get_motor_collection()
                await col.update_one({"_id": ObjectId(cid)}, {"$set": {"likes": count}})
            except Exception:
                pass
        print("[Migration] Likes resynchronises depuis la collection likes")
    except Exception as e:
        print(f"[Migration] Erreur resync likes: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation
    await init_db()
    await cache_manager.connect()
    
    # Initialiser Firebase Admin SDK
    from app.services.push_notification_service import _init_firebase
    _init_firebase()

    # Migration: initialiser likes=0 pour les documents qui n'ont pas ce champ
    await _migrate_likes_field()

    # Démarrer le scheduler CRON pour les tâches automatiques
    start_scheduler()
    
    yield
    
    # Cleanups
    stop_scheduler()
    await cache_manager.disconnect()

app = FastAPI(
    title="BF1 TV API",
    version="2.0.0",
    description="API professionnelle pour l'application BF1 TV - Architecture RESTful",
    lifespan=lifespan,
    docs_url=None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json",
    redirect_slashes=False
)

# Middlewares
# RateLimitMiddleware désactivé pour accepter toutes les requêtes
# app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(GZipMiddleware, minimum_size=1000)
setup_cors(app)
setup_error_handlers(app)
setup_middlewares(app)

# Middleware de résilience - empêche le serveur de planter
app.middleware("http")(resilience_middleware)

# Router principal API v1
api_v1_router = APIRouter(prefix="/api/v1")

# ─── 1. Auth & Utilisateurs (priorité maximale) ───────────────────────────────
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(username_generator.router, prefix="/username", tags=["Username Generator"])
api_v1_router.include_router(user_settings.router, prefix="/settings", tags=["User Settings"])

# ─── 2. Contenu principal ─────────────────────────────────────────────────────
api_v1_router.include_router(breakingNews.router, prefix="/news", tags=["News"])
api_v1_router.include_router(liveStream.router, prefix="/livestream", tags=["Live Stream"])
api_v1_router.include_router(programs.router, prefix="/programs", tags=["Programs"])
api_v1_router.include_router(jtandmag.router, prefix="/jtandmag", tags=["JT and Magazines"])
api_v1_router.include_router(reportage.router, prefix="/reportage", tags=["Reportages"])
api_v1_router.include_router(reel.router, prefix="/reels", tags=["Reels"])
api_v1_router.include_router(divertissement.router, prefix="/divertissement", tags=["Divertissement"])
api_v1_router.include_router(sport.router, prefix="/sports", tags=["Sports"])
# api_v1_router.include_router(series.router, prefix="/tv", tags=["TV Series"])
api_v1_router.include_router(tele_realite.router, prefix="/tele-realite", tags=["Télé Réalité & Événements"])
api_v1_router.include_router(archives.router, prefix="/archives", tags=["Archives"])
# api_v1_router.include_router(movies.router, prefix="/movies", tags=["Movies"])


# ─── 2. Abonnements & Paiements ───────────────────────────────────────────────
api_v1_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_v1_router.include_router(subscription_plans.router, prefix="/subscription-plans", tags=["Subscription Plans"])
api_v1_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_v1_router.include_router(premium.router, prefix="/premium", tags=["Premium"])


# ─── 3. Interactions utilisateur ──────────────────────────────────────────────
api_v1_router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
api_v1_router.include_router(likes.router, prefix="/likes", tags=["Likes"])
api_v1_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_v1_router.include_router(shares.router, prefix="/shares", tags=["Shares"])
api_v1_router.include_router(views.router, prefix="/views", tags=["Views"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(messages.router, prefix="/messages", tags=["Messages"])

# ─── 4. Recherche & Navigation ────────────────────────────────────────────────
api_v1_router.include_router(search.router, prefix="/search", tags=["Search"])
api_v1_router.include_router(carousel.router, prefix="/carousel", tags=["Carousel"])
api_v1_router.include_router(section_categories.router, prefix="/section-categories", tags=["Section Categories"])
api_v1_router.include_router(emission_categories.router, prefix="/emission-categories", tags=["Emission Categories"])

# ─── 5. Abonnements & Paiements ───────────────────────────────────────────────
api_v1_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_v1_router.include_router(subscription_plans.router, prefix="/subscription-plans", tags=["Subscription Plans"])
api_v1_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_v1_router.include_router(premium.router, prefix="/premium", tags=["Premium"])

# ─── 6. Support & Informations ────────────────────────────────────────────────
api_v1_router.include_router(support.router, prefix="/support", tags=["Support"])
api_v1_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_v1_router.include_router(about.router, prefix="/about", tags=["About"])

# ─── 7. Admin & Utilitaires ───────────────────────────────────────────────────
api_v1_router.include_router(upload.router, prefix="/upload", tags=["Upload"])
# api_v1_router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
api_v1_router.include_router(stats.router, prefix="/stats", tags=["Statistics"])

# WebSocket router
app.include_router(websocket.router)

# Monter le router API v1
app.include_router(api_v1_router)

# Static files
static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Route Swagger UI personnalisée
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Routes racine
@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Bienvenue sur l'API BF1 TV",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/docs",
        "api_base": "/api/v1"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "cache_enabled": settings.REDIS_ENABLED
    }

@app.get("/api", tags=["API Info"])
async def api_info():
    return {
        "name": "BF1 TV API",
        "version": "2.0.0",
        "available_versions": ["v1"],
        "current_version": "v1",
        "base_url": "/api/v1",
        "documentation": "/docs",
        "endpoints": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    }
