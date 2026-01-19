from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.database import get_db
from app.models import Transaction, Account, Category, TransactionType
from app.auth import get_current_user
from app.services.transaction_service import TransactionService
from app.config import settings
from datetime import datetime, date
import os
import uuid

router = APIRouter(prefix="/transactions")
templates = Jinja2Templates(directory="app/templates")
templates.env.globals.update(now=datetime.now)


@router.get("", response_class=HTMLResponse)
async def list_transactions(
    request: Request,
    db: Session = Depends(get_db),
    search: str = None,
    category_id: int = None,
    account_id: int = None,
    type: str = None,
    date_from: str = None,
    date_to: str = None
):
    """List and filter transactions"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Base query
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Transaction.description.ilike(f"%{search}%"),
                Transaction.notes.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    if account_id:
        query = query.filter(
            or_(
                Transaction.source_account_id == account_id,
                Transaction.dest_account_id == account_id
            )
        )
    
    if type:
        query = query.filter(Transaction.type == type)
    
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, "%Y-%m-%d").date())
    
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, "%Y-%m-%d").date())
    
    # Order by date descending
    transactions = query.order_by(Transaction.date.desc(), Transaction.created_at.desc()).all()
    
    # Get accounts and categories for filters
    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    categories = db.query(Category).filter(Category.user_id == user.id).all()
    
    return templates.TemplateResponse("transactions/list.html", {
        "request": request,
        "user": user,
        "transactions": transactions,
        "accounts": accounts,
        "categories": categories,
        "search": search or "",
        "selected_category": category_id,
        "selected_account": account_id,
        "selected_type": type,
        "date_from": date_from or "",
        "date_to": date_to or ""
    })


@router.post("/create")
async def create_transaction(
    request: Request,
    transaction_type: str = Form(...),
    amount: float = Form(...),
    transaction_date: str = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    category_id: int = Form(None),
    source_account_id: int = Form(None),
    dest_account_id: int = Form(None),
    receipt: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Parse date
    txn_date = datetime.strptime(transaction_date, "%Y-%m-%d").date()
    
    # Handle receipt upload
    receipt_path = None
    if receipt and receipt.filename:
        settings.create_upload_dirs()
        # Generate unique filename
        ext = os.path.splitext(receipt.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(settings.RECEIPTS_DIR, filename)
        
        # Save file
        with open(filepath, "wb") as f:
            content = await receipt.read()
            f.write(content)
        
        receipt_path = filepath
    
    # Create transaction data
    transaction_data = {
        "type": TransactionType(transaction_type.lower()),
        "amount": amount,
        "date": txn_date,
        "description": description,
        "notes": notes,
        "category_id": category_id if category_id else None,
        "source_account_id": source_account_id if source_account_id else None,
        "dest_account_id": dest_account_id if dest_account_id else None,
        "receipt_path": receipt_path
    }
    
    # Create transaction and update balances
    TransactionService.create_transaction(db, transaction_data, user.id)
    
    return RedirectResponse(url="/transactions", status_code=302)


@router.post("/{transaction_id}/update")
async def update_transaction(
    request: Request,
    transaction_id: int,
    amount: float = Form(...),
    transaction_date: str = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    category_id: int = Form(None),
    db: Session = Depends(get_db)
):
    """Update transaction"""
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user.id
    ).first()
    
    if not transaction:
        return JSONResponse({"error": "Transaction not found"}, status_code=404)
    
    # Parse date
    txn_date = datetime.strptime(transaction_date, "%Y-%m-%d").date()
    
    # Update data
    update_data = {
        "amount": amount,
        "date": txn_date,
        "description": description,
        "notes": notes,
        "category_id": category_id if category_id else None
    }
    
    # Update transaction and recalculate balances
    TransactionService.update_transaction(db, transaction, update_data)
    
    return JSONResponse({"success": True})


@router.post("/{transaction_id}/delete")
async def delete_transaction(
    request: Request,
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """Delete transaction"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user.id
    ).first()
    
    if transaction:
        # Delete receipt file if exists
        if transaction.receipt_path and os.path.exists(transaction.receipt_path):
            try:
                os.remove(transaction.receipt_path)
            except:
                pass
        
        # Delete transaction and revert balances
        TransactionService.delete_transaction(db, transaction)
    
    return RedirectResponse(url="/transactions", status_code=302)
