from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

# ===== SERIES SCHEMAS =====
class SeriesBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    genre: List[str] = Field(default=[])
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    country: str = Field(default="Sénégal")
    language: str = Field(default="Français")
    status: str = Field(default="ongoing")  # ongoing, completed, cancelled, hiatus
    rating: str = Field(default="G")  # G, PG, PG-13, R, NC-17
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    trailer_url: Optional[str] = None
    is_premium: bool = Field(default=False)
    required_subscription_category: Optional[str] = Field(None, description="Catégorie d'abonnement requise: basic, standard, premium")
    allow_comments: bool = Field(default=True)
    cast: List[str] = Field(default=[])
    crew: List[str] = Field(default=[])
    production_company: Optional[str] = None
    network: str = Field(default="BF1")
    episode_duration: int = Field(default=45, ge=1, le=300)
    total_seasons: int = Field(default=0, ge=0)

class SeriesCreate(SeriesBase):
    pass

class SeriesUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    genre: Optional[List[str]] = None
    release_year: Optional[int] = Field(None, ge=1900, le=2030)
    country: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    trailer_url: Optional[str] = None
    is_premium: Optional[bool] = None
    required_subscription_category: Optional[str] = None
    allow_comments: Optional[bool] = None
    cast: Optional[List[str]] = None
    crew: Optional[List[str]] = None
    production_company: Optional[str] = None
    network: Optional[str] = None
    episode_duration: Optional[int] = Field(None, ge=1, le=300)
    total_seasons: Optional[int] = Field(None, ge=0)

class SeriesOut(SeriesBase):
    id: str
    total_episodes: int = 0
    views_count: int = 0
    likes_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True

# ===== SEASON SCHEMAS =====
class SeasonBase(BaseModel):
    season_number: int = Field(..., ge=1)
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    status: str = Field(default="upcoming")  # upcoming, airing, completed

class SeasonCreate(SeasonBase):
    series_id: str

class SeasonUpdate(BaseModel):
    season_number: Optional[int] = Field(None, ge=1)
    title: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    status: Optional[str] = None

class SeasonOut(SeasonBase):
    id: str
    series_id: str
    episode_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", "series_id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True

# ===== EPISODE SCHEMAS =====
class EpisodeBase(BaseModel):
    episode_number: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, ge=1, le=300)  # minutes
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    release_date: Optional[datetime] = None
    status: str = Field(default="upcoming")  # upcoming, available, unavailable
    is_premium: bool = Field(default=False)

class EpisodeCreate(EpisodeBase):
    series_id: str
    season_id: str

class EpisodeUpdate(BaseModel):
    episode_number: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    duration: Optional[int] = Field(None, ge=1, le=300)
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    release_date: Optional[datetime] = None
    status: Optional[str] = None
    is_premium: Optional[bool] = None

class EpisodeOut(EpisodeBase):
    id: str
    series_id: str
    season_id: str
    views_count: int = 0
    likes_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", "series_id", "season_id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True

# ===== RESPONSE SCHEMAS =====
class SeriesListResponse(BaseModel):
    series: List[SeriesOut]
    total: int
    page: int
    pages: int

class SeasonListResponse(BaseModel):
    seasons: List[SeasonOut]
    total: int

class EpisodeListResponse(BaseModel):
    episodes: List[EpisodeOut]
    total: int
    page: int
    pages: int