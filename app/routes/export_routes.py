from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction
from app.auth import get_current_user
import pandas as pd
import io
from datetime import datetime

router = APIRouter(prefix="/export")


@router.get("/csv")
async def export_csv(
    request: Request,
    db: Session = Depends(get_db),
    date_from: str = None,
    date_to: str = None
):
    """Export transactions as CSV"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get transactions
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, "%Y-%m-%d").date())
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, "%Y-%m-%d").date())
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Convert to DataFrame
    data = []
    for txn in transactions:
        data.append({
            'Date': txn.date.strftime('%Y-%m-%d'),
            'Type': txn.type.value,
            'Amount': txn.amount,
            'Description': txn.description or '',
            'Category': txn.category.name if txn.category else '',
            'Source Account': txn.source_account.name if txn.source_account else '',
            'Destination Account': txn.dest_account.name if txn.dest_account else '',
            'Notes': txn.notes or ''
        })
    
    df = pd.DataFrame(data)
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Return as download
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/excel")
async def export_excel(
    request: Request,
    db: Session = Depends(get_db),
    date_from: str = None,
    date_to: str = None
):
    """Export transactions as Excel"""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get transactions
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    
    if date_from:
        query = query.filter(Transaction.date >= datetime.strptime(date_from, "%Y-%m-%d").date())
    if date_to:
        query = query.filter(Transaction.date <= datetime.strptime(date_to, "%Y-%m-%d").date())
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Convert to DataFrame
    data = []
    for txn in transactions:
        data.append({
            'Date': txn.date.strftime('%Y-%m-%d'),
            'Type': txn.type.value,
            'Amount': txn.amount,
            'Description': txn.description or '',
            'Category': txn.category.name if txn.category else '',
            'Source Account': txn.source_account.name if txn.source_account else '',
            'Destination Account': txn.dest_account.name if txn.dest_account else '',
            'Notes': txn.notes or ''
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Transactions', index=False)
    output.seek(0)
    
    # Return as download
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=transactions_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )
