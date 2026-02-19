from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from app.models.movie import Movie
from app.models.user import User
from app.models.show import Show
from app.models.favorite import Favorite
from app.models.like import Like
from app.models.comment import Comment
from app.models.breakingNews import BreakingNews
from app.models.notification import Notification
from app.models.subscription import Subscription
from app.models.message import Message
from app.models.subscription_plan import SubscriptionPlan
from app.models.divertissement import Divertissement
from app.models.popularPrograms import PopularPrograms
from app.models.reel import Reel
from app.models.reportage import Reportage
from app.models.jtandmag import JTandMag
from app.models.share import Share
from app.models.program import Program, LiveChannel, ProgramReminder
from app.models.user_settings import UserSettings
from app.models.support import SupportTicket, FAQ
from app.models.about import AppInfo, TeamMember
from app.models.archive import Archive
from app.models.archive_purchase import ArchivePurchase
from app.models.payment_method import PaymentMethod
from app.models.recording import RecordingSession
from app.models.category import Category
from app.models.emission import Emission
from app.api.contact import ContactMessageDoc
from app.models import enums
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    db_url = os.getenv("MONGODB_URI", "MONGODB_URI=mongodb://localhost:27017/Bf1_db_dev")
    db_name = os.getenv("MONGODB_DBNAME", "Bf1_db_dev")
    client = AsyncIOMotorClient(db_url)
    await init_beanie(
        database=client[db_name],
        document_models=[
            Movie, User, Show, Favorite, Like, Comment, BreakingNews, Notification,
            Subscription, SubscriptionPlan, Message, Divertissement, PopularPrograms, Reel, Reportage, JTandMag, Share,
            Program, LiveChannel, ProgramReminder, UserSettings, SupportTicket, FAQ, AppInfo, TeamMember, Archive,
            ArchivePurchase, PaymentMethod, RecordingSession, Category, Emission, ContactMessageDoc
        ]
    )
