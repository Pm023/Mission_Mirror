import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mission Mirror - Junior Astronaut Mission Trainer"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mission_mirror.db")
    
    # Optional LLM integration
    LLM_PROVIDER: Optional[str] = os.getenv("LLM_PROVIDER", None)
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", None)
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
