from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./nutrition_scanner.db"
    INFERENCE_SERVICE_URL: str = "http://inference:8001"
    STORAGE_PROVIDER: str = "local" # local, supabase
    STORAGE_LOCAL_DIR: str = "./uploads"
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"
    MAX_IMAGE_SIZE_MB: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
