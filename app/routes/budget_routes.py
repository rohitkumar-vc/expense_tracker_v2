from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Budget, Category
from app.auth import get_current_user
from app.services.analytics_service import AnalyticsService
from datetime import datetime

router = APIRouter(prefix="/budgets")
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_budgets(request: Request, db: Session = Depends(get_db)):
    """List budgets with spending comparison"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get current month budgets
    now = datetime.now()
    budgets = db.query(Budget).filter(
        Budget.user_id == user.id,
        Budget.month == now.month,
        Budget.year == now.year
    ).all()
    
    # Get budget status (includes spending)
    budget_status = AnalyticsService.get_budget_status(db, user.id)
    
    # Get categories for creating new budgets
    expense_categories = db.query(Category).filter(
        Category.user_id == user.id,
        Category.type == "expense"
    ).all()
    
    return templates.TemplateResponse("budgets/list.html", {
        "request": request,
        "user": user,
        "budgets": budgets,
        "budget_status": budget_status,
        "expense_categories": expense_categories,
        "current_month": now.month,
        "current_year": now.year
    })


@router.post("/create")
async def create_budget(
    request: Request,
    category_id: int = Form(...),
    amount: float = Form(...),
    month: int = Form(...),
    year: int = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Check if budget already exists for this category/month/year
    existing = db.query(Budget).filter(
        Budget.user_id == user.id,
        Budget.category_id == category_id,
        Budget.month == month,
        Budget.year == year
    ).first()
    
    if existing:
        # Update existing
        existing.amount = amount
        db.commit()
    else:
        # Create new
        budget = Budget(
            user_id=user.id,
            category_id=category_id,
            amount=amount,
            month=month,
            year=year
        )
        db.add(budget)
        db.commit()
    
    return RedirectResponse(url="/budgets", status_code=302)


@router.post("/{budget_id}/update")
async def update_budget(
    request: Request,
    budget_id: int,
    amount: float = Form(...),
    db: Session = Depends(get_db)
):
    """Update budget amount"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user.id
    ).first()
    
    if not budget:
        return JSONResponse({"error": "Budget not found"}, status_code=404)
    
    budget.amount = amount
    db.commit()
    
    return JSONResponse({"success": True})


@router.post("/{budget_id}/delete")
async def delete_budget(
    request: Request,
    budget_id: int,
    db: Session = Depends(get_db)
):
    """Delete budget"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user.id
    ).first()
    
    if budget:
        db.delete(budget)
        db.commit()
    
    return RedirectResponse(url="/budgets", status_code=302)
