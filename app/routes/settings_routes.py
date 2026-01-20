from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/settings")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def general_settings(request: Request, db: Session = Depends(get_db)):
    """General settings page (Dark Mode, etc.)"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("settings/general.html", {
        "request": request,
        "user": user
    })
