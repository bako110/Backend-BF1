"""
Schémas Pydantic pour les émissions
Définit la validation et la sérialisation des données des émissions
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId


class CategoryEnum(str, Enum):
    """Énumération des catégories d'émissions valides"""
    toutes = "toutes"
    jt = "jt"
    magazines = "magazines"
    documentaires = "documentaires"
    divertissement = "divertissement"
    sport = "sport"
    emission = "emission"


class EmissionBase(BaseModel):
    """Schéma de base pour les émissions"""
    title: str = Field(..., min_length=1, max_length=255, description="Titre de l'émission")
    description: Optional[str] = Field(None, max_length=2000, description="Description de l'émission")
    category: CategoryEnum = Field(..., description="Catégorie de l'émission")
    subcategory: Optional[str] = Field(None, max_length=50, description="Sous-catégorie")
    image: Optional[str] = Field(None, max_length=500, description="URL de l'image principale")
    thumbnail: Optional[str] = Field(None, max_length=500, description="URL de la miniature")
    video_url: Optional[str] = Field(None, max_length=500, description="URL de la vidéo")
    duration: Optional[int] = Field(None, ge=0, description="Durée en secondes")
    date: Optional[datetime] = Field(None, description="Date de diffusion")
    presenter: Optional[str] = Field(None, max_length=255, description="Présentateur")
    tags: Optional[List[str]] = Field(default=[], description="Liste des tags")
    featured: Optional[bool] = Field(False, description="Émission en vedette")
    is_new: Optional[bool] = Field(False, description="Nouvelle émission")
    is_active: Optional[bool] = Field(True, description="Émission active")

    @validator('tags')
    def validate_tags(cls, v):
        """Valide que les tags sont des chaînes de caractères"""
        if v is None:
            return []
        return [tag.strip() for tag in v if isinstance(tag, str) and tag.strip()]

    @validator('image', 'thumbnail', 'video_url')
    def validate_urls(cls, v):
        """Valide que les URLs sont correctes"""
        if v is None:
            return v
        # Validation simple d'URL
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL invalide')
        return v


class EmissionCreate(EmissionBase):
    """Schéma pour la création d'une émission"""
    pass


class EmissionUpdate(BaseModel):
    """Schéma pour la mise à jour d'une émission"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    category: Optional[CategoryEnum] = None
    subcategory: Optional[str] = Field(None, max_length=50)
    image: Optional[str] = Field(None, max_length=500)
    thumbnail: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    duration: Optional[int] = Field(None, ge=0)
    date: Optional[datetime] = None
    presenter: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    featured: Optional[bool] = None
    is_new: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator('tags')
    def validate_tags(cls, v):
        if v is None:
            return v
        return [tag.strip() for tag in v if isinstance(tag, str) and tag.strip()]


class EmissionResponse(EmissionBase):
    """Schéma pour la réponse des émissions"""
    id: str
    views: int = Field(default=0, ge=0, description="Nombre de vues")
    likes: int = Field(default=0, ge=0, description="Nombre de likes")
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("id", pre=True, always=True)
    def str_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True


class EmissionList(BaseModel):
    """Schéma pour la liste des émissions"""
    emissions: List[EmissionResponse]
    total: int = Field(..., ge=0, description="Nombre total d'émissions")
    page: int = Field(..., ge=1, description="Page actuelle")
    per_page: int = Field(..., ge=1, le=100, description="Éléments par page")
    total_pages: int = Field(..., ge=0, description="Nombre total de pages")


class EmissionStats(BaseModel):
    """Schéma pour les statistiques d'une émission"""
    id: str
    views: int
    likes: int
    last_viewed: Optional[datetime] = None


class CategoryInfo(BaseModel):
    """Schéma pour les informations de catégorie"""
    id: str
    name: str
    icon: str
    count: int = Field(..., ge=0, description="Nombre d'émissions dans cette catégorie")


class CategoryList(BaseModel):
    """Schéma pour la liste des catégories"""
    categories: List[CategoryInfo]
    total_categories: int


class SearchRequest(BaseModel):
    """Schéma pour la requête de recherche"""
    query: str = Field(..., min_length=1, max_length=100, description="Terme de recherche")
    category: Optional[CategoryEnum] = Field(None, description="Filtrer par catégorie")
    limit: Optional[int] = Field(20, ge=1, le=100, description="Limite de résultats")
    offset: Optional[int] = Field(0, ge=0, description="Offset pour la pagination")


class LikeRequest(BaseModel):
    """Schéma pour la gestion des likes"""
    action: str = Field(..., pattern="^(add|remove)$", description="Action: add ou remove")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur (optionnel)")


class ViewIncrementRequest(BaseModel):
    """Schéma pour l'incrémentation des vues"""
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur (optionnel)")
    session_id: Optional[str] = Field(None, description="ID de session pour utilisateurs non authentifiés")
