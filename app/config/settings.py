from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Charger les variables d'environnement AVANT de créer la classe
load_dotenv()

class Settings(BaseSettings):
    # MongoDB - Utiliser os.getenv() comme fallback explicite
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bf1_db_dev")
    MONGODB_DBNAME: str = os.getenv("MONGODB_DBNAME", "bf1_db_dev")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key_change_in_production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Email
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.mailtrap.io")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "2525"))
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@bf1.com")
    
    # Redis
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # CORS - Utiliser directement os.getenv() pour éviter les problèmes
    ALLOWED_ORIGINS_STR: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000"))
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Récupérer ALLOWED_ORIGINS_STR depuis .env si non défini
        if self.ALLOWED_ORIGINS_STR is None:
            self.ALLOWED_ORIGINS_STR = os.getenv(
                "ALLOWED_ORIGINS_STR", 
                "http://localhost:3000,http://127.0.0.1:3000"
            )
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Convertir la chaîne ALLOWED_ORIGINS_STR en liste"""
        if not self.ALLOWED_ORIGINS_STR:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",") if origin.strip()]
    
    @property
    def DEBUG(self) -> bool:
        """Mode debug basé sur l'environnement"""
        return self.ENVIRONMENT.lower() in ["development", "dev", "local"]

# Créer l'instance settings
settings = Settings()

# Vérifier les valeurs chargées (pour debug)
if __name__ == "__main__":
    print("=" * 50)
    print("VÉRIFICATION DES VARIABLES D'ENVIRONNEMENT")
    print("=" * 50)
    print(f"MONGODB_URI: {settings.MONGODB_URI[:50]}...")
    print(f"MONGODB_DBNAME: {settings.MONGODB_DBNAME}")
    print(f"JWT_SECRET_KEY: {'***' if settings.JWT_SECRET_KEY else 'Non défini'}")
    print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
    print("=" * 50)