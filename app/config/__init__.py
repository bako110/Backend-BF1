from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.models.movie import Movie
from app.models.user import User
from app.models.show import Show
from app.models.favorite import Favorite
from app.models.like import Like
from app.models.comment import Comment
from app.models.news import News
from app.models.notification import Notification
from app.models.subscription import Subscription
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    db_url = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bf1_db")
    db_name = os.getenv("MONGODB_DBNAME", "bf1_db")
    client = AsyncIOMotorClient(db_url)
    await init_beanie(
        database=client[db_name],
        document_models=[
            Movie, User, Show, Favorite, Like, Comment, News, Notification, Subscription
        ]
    )
