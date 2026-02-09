import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from app.config import init_db
from app.config.settings import settings
from app.core.cors import setup_cors
from app.core.error_handlers import setup_error_handlers
from app.core.middlewares import setup_middlewares
from app.utils.cache import cache_manager
from app.utils.rate_limiter import RateLimitMiddleware

from app.api import (
    shows, movies, users, favorites, breakingNews, notifications, subscriptions, payments, premium,
    contact, comments, likes, messages, interview, reel, replay, trendingShow, popularPrograms, shares,
    programs, stats, user_settings, support, about, archives, liveStream
)
from app.api import websocket
from app.api import uploads
from app.api import subscription_plans

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialisation
    await init_db()
    await cache_manager.connect()
    yield
    # Cleanups
    await cache_manager.disconnect()

app = FastAPI(
    title="BF1 TV API",
    version="2.0.0",
    description="API professionnelle pour l'application BF1 TV - Architecture RESTful",
    lifespan=lifespan,
    docs_url=None,  # Désactivé pour créer une version personnalisée
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json"
)

# Middlewares (ordre important - CORS doit être appliqué DERNIER pour exécuter PREMIER)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(GZipMiddleware, minimum_size=1000)
setup_cors(app)
setup_error_handlers(app)
setup_middlewares(app)

# Router principal API v1
api_v1_router = APIRouter(prefix="/api/v1")

# Inclusion des routers avec préfixes professionnels
api_v1_router.include_router(shows.router, prefix="/shows", tags=["Shows"])
api_v1_router.include_router(movies.router, prefix="/movies", tags=["Movies"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
api_v1_router.include_router(breakingNews.router, prefix="/news", tags=["News"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
api_v1_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_v1_router.include_router(premium.router, prefix="/premium", tags=["Premium"])
api_v1_router.include_router(contact.router, prefix="/contact", tags=["Contact"])
api_v1_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_v1_router.include_router(likes.router, prefix="/likes", tags=["Likes"])
api_v1_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_v1_router.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])
api_v1_router.include_router(subscription_plans.router, prefix="/subscription-plans", tags=["Subscription Plans"])
api_v1_router.include_router(interview.router, prefix="/interviews", tags=["Interviews"])
api_v1_router.include_router(reel.router, prefix="/reels", tags=["Reels"])
api_v1_router.include_router(replay.router, prefix="/replays", tags=["Replays"])
api_v1_router.include_router(trendingShow.router, prefix="/trending-shows", tags=["Trending Shows"])
api_v1_router.include_router(popularPrograms.router, prefix="/popular-programs", tags=["Popular Programs"])
api_v1_router.include_router(programs.router, prefix="/programs", tags=["Programs"])
api_v1_router.include_router(shares.router, prefix="/shares", tags=["Shares"])
api_v1_router.include_router(stats.router, prefix="/stats", tags=["Statistics"])
api_v1_router.include_router(user_settings.router, prefix="/settings", tags=["User Settings"])
api_v1_router.include_router(support.router, prefix="/support", tags=["Support"])
api_v1_router.include_router(about.router, prefix="/about", tags=["About"])
api_v1_router.include_router(archives.router, prefix="/archives", tags=["Archives"])
api_v1_router.include_router(liveStream.router, prefix="/live-stream", tags=["Live Stream"])

# Monter le router WebSocket directement (sans préfixe API v1)
app.include_router(websocket.router)

# Monter le router API v1
app.include_router(api_v1_router)

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

# Routes racine (hors versioning)
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
