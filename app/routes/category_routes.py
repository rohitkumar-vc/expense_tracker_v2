from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category, CategoryType
from app.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/settings/categories", response_class=HTMLResponse)
async def categories_settings(request: Request, db: Session = Depends(get_db)):
    """Category management page"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    income_categories = [c for c in categories if c.type == CategoryType.INCOME]
    expense_categories = [c for c in categories if c.type == CategoryType.EXPENSE]
    
    return templates.TemplateResponse("settings/categories.html", {
        "request": request,
        "user": user,
        "income_categories": income_categories,
        "expense_categories": expense_categories
    })


@router.post("/categories/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    category_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new category"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    category = Category(
        user_id=user.id,
        name=name,
        type=CategoryType(category_type.lower()),
        is_system=False
    )
    db.add(category)
    db.commit()
    
    return RedirectResponse(url="/settings/categories", status_code=302)


@router.post("/categories/{category_id}/update")
async def update_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update category name"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user.id
    ).first()
    
    if not category:
        return JSONResponse({"error": "Category not found"}, status_code=404)
    
    category.name = name
    db.commit()
    
    return JSONResponse({"success": True})


@router.post("/categories/{category_id}/delete")
async def delete_category(
    request: Request,
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete category (only custom categories)"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user.id
    ).first()
    
    if category and not category.is_system:
        db.delete(category)
        db.commit()
    
    return RedirectResponse(url="/settings/categories", status_code=302)
