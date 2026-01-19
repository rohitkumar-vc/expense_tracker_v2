from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Account, AccountType
from app.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/accounts")
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def list_accounts(request: Request, db: Session = Depends(get_db)):
    """List all user accounts"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    
    # Separate by type
    bank_accounts = [a for a in accounts if a.type == AccountType.BANK]
    credit_cards = [a for a in accounts if a.type == AccountType.CREDIT_CARD]
    cash_accounts = [a for a in accounts if a.type == AccountType.CASH]
    
    return templates.TemplateResponse("accounts/list.html", {
        "request": request,
        "user": user,
        "bank_accounts": bank_accounts,
        "credit_cards": credit_cards,
        "cash_accounts": cash_accounts
    })


@router.post("/create")
async def create_account(
    request: Request,
    account_type: str = Form(...),
    name: str = Form(...),
    bank_name: str = Form(None),
    account_number: str = Form(None),
    initial_balance: float = Form(0.0),
    total_limit: float = Form(0.0),
    billing_date: int = Form(None),
    due_date: int = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    account = Account(
        user_id=user.id,
        type=AccountType(account_type.lower()),
        name=name
    )
    
    if account_type == "bank":
        account.bank_name = bank_name
        account.account_number = account_number
        account.initial_balance = initial_balance
        account.current_balance = initial_balance
    elif account_type == "credit_card":
        account.total_limit = total_limit
        account.used_amount = 0.0
        account.billing_date = billing_date
        account.due_date = due_date
    elif account_type == "cash":
        account.initial_balance = initial_balance
        account.current_balance = initial_balance
    
    db.add(account)
    db.commit()
    
    return RedirectResponse(url="/accounts", status_code=302)


@router.post("/{account_id}/update")
async def update_account(
    request: Request,
    account_id: int,
    name: str = Form(...),
    bank_name: str = Form(None),
    account_number: str = Form(None),
    total_limit: float = Form(None),
    billing_date: int = Form(None),
    due_date: int = Form(None),
    db: Session = Depends(get_db)
):
    """Update account details"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == user.id
    ).first()
    
    if not account:
        return JSONResponse({"error": "Account not found"}, status_code=404)
    
    account.name = name
    
    if account.type == AccountType.BANK:
        account.bank_name = bank_name
        account.account_number = account_number
    elif account.type == AccountType.CREDIT_CARD:
        if total_limit is not None:
            account.total_limit = total_limit
        if billing_date is not None:
            account.billing_date = billing_date
        if due_date is not None:
            account.due_date = due_date
    
    db.commit()
    
    return JSONResponse({"success": True})


@router.post("/{account_id}/delete")
async def delete_account(
    request: Request,
    account_id: int,
    db: Session = Depends(get_db)
):
    """Delete account"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == user.id
    ).first()
    
    if account:
        db.delete(account)
        db.commit()
    
    return RedirectResponse(url="/accounts", status_code=302)
