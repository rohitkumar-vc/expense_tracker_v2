import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./expense_manager.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    RECEIPTS_DIR: str = os.path.join(UPLOAD_DIR, "receipts")
    
    # Session settings
    SESSION_COOKIE_NAME: str = "expense_session"
    SESSION_MAX_AGE: int = 86400 * 7  # 7 days
    
    # Pagination
    ITEMS_PER_PAGE: int = 20
    
    @classmethod
    def create_upload_dirs(cls):
        """Create upload directories if they don't exist"""
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        os.makedirs(cls.RECEIPTS_DIR, exist_ok=True)

settings = Settings()
