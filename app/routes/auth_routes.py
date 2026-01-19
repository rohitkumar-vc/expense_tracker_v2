from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import verify_password, hash_password, get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    """Root route - redirect to dashboard if logged in, else login"""
    user = get_current_user(request, db)
    if user:
        if user.role == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/dashboard"):
    """Display login page"""
    # If already logged in, redirect
    if request.session.get("user_id"):
        return RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next": next,
        "error": None
    })


@router.post("/login")
async def login(
    request: Request,
    user_id: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
    db: Session = Depends(get_db)
):
    """Process login"""
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password",
            "next": next
        }, status_code=400)
    
    if not user.is_active:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Account is disabled. Please contact administrator.",
            "next": next
        }, status_code=400)
    
    # Set session
    request.session["user_id"] = user.id
    request.session["user_role"] = user.role.value
    request.session["must_change_password"] = user.must_change_password
    
    # Redirect to password change if required
    if user.must_change_password:
        return RedirectResponse(url="/change-password", status_code=status.HTTP_302_FOUND)
    
    # Redirect based on role
    if user.role.value == "admin" and next == "/dashboard":
        return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
    
    return RedirectResponse(url=next, status_code=status.HTTP_302_FOUND)


@router.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request, db: Session = Depends(get_db)):
    """Display change password page"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("change_password.html", {
        "request": request,
        "user": user,
        "error": None,
        "success": None
    })


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process password change"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Verify current password
    if not verify_password(current_password, user.password_hash):
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "user": user,
            "error": "Current password is incorrect",
            "success": None
        }, status_code=400)
    
    # Check new password confirmation
    if new_password != confirm_password:
        return templates.TemplateResponse("change_password.html", {
            "request": request,
            "user": user,
            "error": "New passwords do not match",
            "success": None
        }, status_code=400)
    
    # Update password
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.commit()
    
    # Update session
    request.session["must_change_password"] = False
    
    # Redirect to appropriate dashboard
    if user.role.value == "admin":
        return RedirectResponse(url="/admin/dashboard?success=Password changed successfully", status_code=status.HTTP_302_FOUND)
    
    return RedirectResponse(url="/dashboard?success=Password changed successfully", status_code=status.HTTP_302_FOUND)
