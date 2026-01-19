from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Transaction, Account, Budget, Category, AccountType, TransactionType
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Analytics and reporting calculations"""
    
    @staticmethod
    def calculate_net_worth(db: Session, user_id: int) -> float:
        """Calculate total net worth (Banks + Cash - CC Debt)"""
        accounts = db.query(Account).filter(Account.user_id == user_id).all()
        
        total = 0.0
        for account in accounts:
            if account.type == AccountType.BANK or account.type == AccountType.CASH:
                total += account.current_balance
            elif account.type == AccountType.CREDIT_CARD:
                total -= account.used_amount  # Subtract debt
        
        return total
    
    @staticmethod
    def get_monthly_income(db: Session, user_id: int, month: int = None, year: int = None) -> float:
        """Get total income for a specific month"""
        if month is None or year is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar()
        
        return total or 0.0
    
    @staticmethod
    def get_monthly_expense(db: Session, user_id: int, month: int = None, year: int = None) -> float:
        """Get total expenses for a specific month"""
        if month is None or year is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar()
        
        return total or 0.0
    
    @staticmethod
    def get_expense_by_category(db: Session, user_id: int, month: int = None, year: int = None) -> dict:
        """Get expense breakdown by category"""
        if month is None or year is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        results = db.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).group_by(Category.name).all()
        
        return {name: float(total) for name, total in results}
    
    @staticmethod
    def get_weekly_trend(db: Session, user_id: int, weeks: int = 4) -> list:
        """Get weekly spending trend for last N weeks"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()
        
        # Group by week
        weekly_data = defaultdict(float)
        for txn in transactions:
            week_start = txn.date - timedelta(days=txn.date.weekday())
            weekly_data[week_start] += txn.amount
        
        # Format for chart
        result = []
        for i in range(weeks):
            week_start = end_date - timedelta(weeks=weeks-i-1, days=end_date.weekday())
            result.append({
                'week': week_start.strftime('%Y-%m-%d'),
                'amount': weekly_data.get(week_start, 0.0)
            })
        
        return result
    
    @staticmethod
    def get_income_vs_expense_trend(db: Session, user_id: int, months: int = 6) -> list:
        """Get monthly income vs expense for last N months"""
        end_date = datetime.now()
        result = []
        
        for i in range(months):
            target_date = end_date - timedelta(days=30 * (months - i - 1))
            month = target_date.month
            year = target_date.year
            
            income = AnalyticsService.get_monthly_income(db, user_id, month, year)
            expense = AnalyticsService.get_monthly_expense(db, user_id, month, year)
            
            result.append({
                'month': f"{year}-{month:02d}",
                'income': income,
                'expense': expense
            })
        
        return result
    
    @staticmethod
    def get_payment_mode_breakdown(db: Session, user_id: int, month: int = None, year: int = None) -> dict:
        """Get expense breakdown by payment mode"""
        if month is None or year is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        results = db.query(
            Account.type,
            func.sum(Transaction.amount).label('total')
        ).join(
            Transaction, Transaction.source_account_id == Account.id
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).group_by(Account.type).all()
        
        mode_map = {
            AccountType.BANK: "Bank",
            AccountType.CREDIT_CARD: "Credit Card",
            AccountType.CASH: "Cash"
        }
        
        return {mode_map.get(acc_type, str(acc_type)): float(total) for acc_type, total in results}
    
    @staticmethod
    def get_budget_status(db: Session, user_id: int, month: int = None, year: int = None) -> list:
        """Get budget vs actual spending for current month"""
        if month is None or year is None:
            now = datetime.now()
            month = now.month
            year = now.year
        
        budgets = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.month == month,
            Budget.year == year
        ).all()
        
        result = []
        for budget in budgets:
            # Get actual spending
            spent = db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.category_id == budget.category_id,
                extract('month', Transaction.date) == month,
                extract('year', Transaction.date) == year
            ).scalar() or 0.0
            
            result.append({
                'category': budget.category.name,
                'budget': budget.amount,
                'spent': spent,
                'percentage': (spent / budget.amount * 100) if budget.amount > 0 else 0,
                'is_exceeded': spent > budget.amount
            })
        
        return result
