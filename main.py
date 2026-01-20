from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
from app.database import Base, engine
from app.init_db import init_database
import os

# Import routes
from app.routes import (
    auth_routes,
    dashboard_routes,
    admin_routes,
    account_routes,
    transaction_routes,
    budget_routes,
    category_routes,
    export_routes,
    settings_routes
)

# Create FastAPI app
app = FastAPI(
    title="Expense Flow",
    description="Personal expense management system",
    version="1.0.0"
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE
)

# Mount static files
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(admin_routes.router)
app.include_router(account_routes.router)
app.include_router(transaction_routes.router)
app.include_router(budget_routes.router)
app.include_router(category_routes.router)
app.include_router(export_routes.router)
app.include_router(settings_routes.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Expense Flow...")
    
    # Just create tables if they don't exist (won't recreate existing ones)
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables verified/connected")
    except Exception as e:
        print(f"⚠️  Database connection warning: {e}")
    
    print("✅ Expense Flow is ready!")



# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


if __name__ == "__main__":
    # This block is typically used for development with `python main.py`
    # For production, uvicorn is used: `uvicorn main:app --reload`
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
