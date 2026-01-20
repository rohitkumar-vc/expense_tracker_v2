import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./expense_manager.db")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Session settings
    SESSION_COOKIE_NAME: str = "expense_session"
    SESSION_MAX_AGE: int = 86400 * 7  # 7 days
    
    # Pagination
    ITEMS_PER_PAGE: int = 20

settings = Settings()
