from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/bf1_db"
    MONGODB_DBNAME: str = "bf1_db"
    
    # JWT
    JWT_SECRET_KEY: str = "your_jwt_secret_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Email
    EMAIL_HOST: str = "smtp.mailtrap.io"
    EMAIL_PORT: int = 2525
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@bf1.com"
    
    # Redis
    REDIS_ENABLED: bool = False
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS - utiliser str pour éviter le parsing JSON automatique
    ALLOWED_ORIGINS_STR: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Convertir la chaîne ALLOWED_ORIGINS_STR en liste"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(",")]
    
    @property
    def DEBUG(self) -> bool:
        """Mode debug basé sur l'environnement"""
        return self.ENVIRONMENT == "development"

settings = Settings()
