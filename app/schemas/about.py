from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List, Any
from datetime import datetime

class AppInfoBase(BaseModel):
    version: str
    build_number: str
    release_date: datetime
    app_name: str = "BF1 TV"
    description: str
    website: Optional[HttpUrl] = None
    privacy_policy_url: Optional[HttpUrl] = None
    terms_url: Optional[HttpUrl] = None
    facebook_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    instagram_url: Optional[HttpUrl] = None
    youtube_url: Optional[HttpUrl] = None
    support_email: Optional[str] = None
    contact_phone: Optional[str] = None
    features: List[str] = []
    changelog: List[dict] = []


class AppInfoCreate(AppInfoBase):
    pass


class AppInfoUpdate(BaseModel):
    version: Optional[str] = None
    build_number: Optional[str] = None
    release_date: Optional[datetime] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    privacy_policy_url: Optional[HttpUrl] = None
    terms_url: Optional[HttpUrl] = None
    facebook_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    instagram_url: Optional[HttpUrl] = None
    youtube_url: Optional[HttpUrl] = None
    support_email: Optional[str] = None
    contact_phone: Optional[str] = None
    features: Optional[List[str]] = None
    changelog: Optional[List[dict]] = None
    is_active: Optional[bool] = None


class AppInfoOut(AppInfoBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    name: str
    role: str
    bio: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    email: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    order: int = 0


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[HttpUrl] = None
    email: Optional[str] = None
    linkedin_url: Optional[HttpUrl] = None
    twitter_url: Optional[HttpUrl] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class TeamMemberOut(TeamMemberBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v: Any) -> str:
        if hasattr(v, '__str__'):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
