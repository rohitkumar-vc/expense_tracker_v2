from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import User, Account, Transaction, Category, AccountType
from app.auth import get_current_user
from app.services.analytics_service import AnalyticsService
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update(now=datetime.now)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), success: str = None):
    """Main user dashboard"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Redirect admin to admin dashboard
    if user.role.value == "admin":
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    
    # Get analytics data
    net_worth = AnalyticsService.calculate_net_worth(db, user.id)
    monthly_income = AnalyticsService.get_monthly_income(db, user.id)
    monthly_expense = AnalyticsService.get_monthly_expense(db, user.id)
    
    # Get recent transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id
    ).order_by(desc(Transaction.date), desc(Transaction.created_at)).limit(10).all()
    
    # Get budget status
    budget_status = AnalyticsService.get_budget_status(db, user.id)
    
    # Get upcoming credit card payments
    now = datetime.now()
    current_day = now.day
    credit_cards = db.query(Account).filter(
        Account.user_id == user.id,
        Account.type == AccountType.CREDIT_CARD
    ).all()
    
    upcoming_payments = []
    for cc in credit_cards:
        if cc.due_date and cc.used_amount > 0:
            days_until_due = cc.due_date - current_day
            if days_until_due < 0:
                days_until_due += 30  # Rough estimate for next month
            
            upcoming_payments.append({
                'card_name': cc.name,
                'amount': cc.used_amount,
                'due_date': cc.due_date,
                'days_until_due': days_until_due,
                'is_urgent': days_until_due <= 7
            })
    
    # Sort by urgency
    upcoming_payments.sort(key=lambda x: x['days_until_due'])

    # Get accounts and categories for modal
    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "net_worth": net_worth,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "recent_transactions": recent_transactions,
        "budget_status": budget_status,
        "upcoming_payments": upcoming_payments,
        "accounts": accounts,
        "categories": categories,
        "success": success
    })


@router.get("/api/analytics/expense-breakdown")
async def expense_breakdown(request: Request, db: Session = Depends(get_db)):
    """API endpoint for expense breakdown chart data"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    data = AnalyticsService.get_expense_by_category(db, user.id)
    
    return JSONResponse({
        "labels": list(data.keys()),
        "values": list(data.values())
    })


@router.get("/api/analytics/trend")
async def weekly_trend(request: Request, db: Session = Depends(get_db)):
    """API endpoint for weekly spending trend"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    data = AnalyticsService.get_weekly_trend(db, user.id, weeks=4)
    
    return JSONResponse({
        "labels": [item['week'] for item in data],
        "values": [item['amount'] for item in data]
    })


@router.get("/api/analytics/income-vs-expense")
async def income_vs_expense(request: Request, db: Session = Depends(get_db)):
    """API endpoint for income vs expense trend"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    data = AnalyticsService.get_income_vs_expense_trend(db, user.id, months=6)
    
    return JSONResponse({
        "labels": [item['month'] for item in data],
        "income": [item['income'] for item in data],
        "expense": [item['expense'] for item in data]
    })


@router.get("/api/analytics/payment-mode")
async def payment_mode_breakdown(request: Request, db: Session = Depends(get_db)):
    """API endpoint for payment mode breakdown"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    data = AnalyticsService.get_payment_mode_breakdown(db, user.id)
    
    return JSONResponse({
        "labels": list(data.keys()),
        "values": list(data.values())
    })
