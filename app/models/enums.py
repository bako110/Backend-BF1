from enum import Enum


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    MODERATOR = "MODERATOR"


class SubscriptionTier(str, Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    PAST_DUE = "PAST_DUE"
    TRIALING = "TRIALING"


class ContentType(str, Enum):
    LIVE = "LIVE"
    VOD = "VOD"
    NEWS = "NEWS"
    PODCAST = "PODCAST"


class PaymentMethod(str, Enum):
    CARD = "CARD"
    MOBILE_MONEY = "MOBILE_MONEY"
    OPERATOR = "OPERATOR"
    PAYPAL = "PAYPAL"
    BANK_TRANSFER = "BANK_TRANSFER"


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class NotificationChannel(str, Enum):
    PUSH = "PUSH"
    INAPP = "INAPP"
    EMAIL = "EMAIL"
    SMS = "SMS"


class NotificationType(str, Enum):
    BREAKING_NEWS = "BREAKING_NEWS"
    PROGRAM_REMINDER = "PROGRAM_REMINDER"
    NEW_CONTENT = "NEW_CONTENT"
    OFFER = "OFFER"
    SOCIAL = "SOCIAL"
    SYSTEM = "SYSTEM"


class DevicePlatform(str, Enum):
    IOS = "IOS"
    ANDROID = "ANDROID"
    WEB = "WEB"


class ArticleFormat(str, Enum):
    TEXT = "TEXT"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    GALLERY = "GALLERY"
    INFOGRAPHIC = "INFOGRAPHIC"


class VideoQuality(str, Enum):
    AUTO = "AUTO"
    SD = "SD"
    HD = "HD"
    FULL_HD = "FULL_HD"
