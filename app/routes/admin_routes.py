from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, Account, Transaction, Category
from app.auth import get_current_user, hash_password
from datetime import datetime

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), success: str = None, error: str = None):
    """Admin dashboard"""
    user = get_current_user(request, db)
    if not user or user.role != UserRole.ADMIN:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get all users
    users = db.query(User).all()
    
    # System stats
    total_users = len(users)
    active_users = sum(1 for u in users if u.is_active)
    total_accounts = db.query(Account).count()
    total_transactions = db.query(Transaction).count()
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": user,
        "users": users,
        "total_users": total_users,
        "active_users": active_users,
        "total_accounts": total_accounts,
        "total_transactions": total_transactions,
        "success": success,
        "error": error
    })


@router.post("/users/create")
async def create_user(
    request: Request,
    user_id: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    email: str = Form(None),
    role: str = Form("user"),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    admin_user = get_current_user(request, db)
    if not admin_user or admin_user.role != UserRole.ADMIN:
        return RedirectResponse(url="/login", status_code=302)
    
    # Check if user_id already exists
    existing = db.query(User).filter(User.user_id == user_id).first()
    if existing:
        return RedirectResponse(
            url="/admin/dashboard?error=User ID already exists",
            status_code=302
        )
    
    # Create user
    new_user = User(
        user_id=user_id,
        password_hash=hash_password(password),
        role=UserRole.ADMIN if role == "admin" else UserRole.USER,
        name=name,
        email=email,
        is_active=True,
        must_change_password=True
    )
    db.add(new_user)
    db.commit()
    
    # Create default categories for new user
    admin = db.query(User).filter(User.user_id == "adminExpense").first()
    if admin:
        admin_categories = db.query(Category).filter(
            Category.user_id == admin.id,
            Category.is_system == True
        ).all()
        
        for cat in admin_categories:
            user_cat = Category(
                user_id=new_user.id,
                name=cat.name,
                type=cat.type,
                is_system=True
            )
            db.add(user_cat)
        db.commit()
    
    return RedirectResponse(
        url="/admin/dashboard?success=User created successfully",
        status_code=302
    )


@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Enable/disable user"""
    admin_user = get_current_user(request, db)
    if not admin_user or admin_user.role != UserRole.ADMIN:
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    user.is_active = not user.is_active
    db.commit()
    
    return JSONResponse({
        "success": True,
        "is_active": user.is_active
    })


@router.post("/users/{user_id}/delete")
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete user"""
    admin_user = get_current_user(request, db)
    if not admin_user or admin_user.role != UserRole.ADMIN:
        return RedirectResponse(url="/login", status_code=302)
    
    # Don't allow deleting self
    if admin_user.id == user_id:
        return RedirectResponse(
            url="/admin/dashboard?error=Cannot delete your own account",
            status_code=302
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    
    return RedirectResponse(
        url="/admin/dashboard?success=User deleted successfully",
        status_code=302
    )


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    request: Request,
    user_id: int,
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Reset user password"""
    admin_user = get_current_user(request, db)
    if not admin_user or admin_user.role != UserRole.ADMIN:
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=404)
    
    user.password_hash = hash_password(new_password)
    user.must_change_password = True
    db.commit()
    
    return JSONResponse({"success": True})
