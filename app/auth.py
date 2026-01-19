import bcrypt
from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models import User


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def get_current_user(request: Request, db: Session) -> User:
    """Get the current logged-in user from session"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


def login_required(func):
    """Decorator to require login for a route"""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user_id = request.session.get("user_id")
        if not user_id:
            return RedirectResponse(url="/login?next=" + str(request.url.path), status_code=status.HTTP_302_FOUND)
        return await func(request, *args, **kwargs)
    return wrapper


def admin_required(func):
    """Decorator to require admin role for a route"""
    @wraps(func)
    async def wrapper(request: Request, db: Session, *args, **kwargs):
        user = get_current_user(request, db)
        if not user or user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
        return await func(request, db, *args, **kwargs)
    return wrapper
