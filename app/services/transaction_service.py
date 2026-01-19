from sqlalchemy.orm import Session
from app.models import Transaction, Account, AccountType, TransactionType
from datetime import datetime


class TransactionService:
    """Business logic for transaction operations"""
    
    @staticmethod
    def apply_transaction(db: Session, transaction: Transaction):
        """Apply transaction effects to account balances"""
        if transaction.type == TransactionType.INCOME:
            # Income: Increase bank account balance
            if transaction.dest_account_id:
                account = db.query(Account).filter(Account.id == transaction.dest_account_id).first()
                if account and account.type == AccountType.BANK:
                    account.current_balance += transaction.amount
                elif account and account.type == AccountType.CASH:
                    account.current_balance += transaction.amount
        
        elif transaction.type == TransactionType.EXPENSE:
            # Expense: Decrease bank balance OR increase CC usage
            if transaction.source_account_id:
                account = db.query(Account).filter(Account.id == transaction.source_account_id).first()
                if account:
                    if account.type == AccountType.BANK or account.type == AccountType.CASH:
                        account.current_balance -= transaction.amount
                    elif account.type == AccountType.CREDIT_CARD:
                        account.used_amount += transaction.amount
        
        elif transaction.type == TransactionType.TRANSFER:
            # Transfer: Decrease source, adjust destination
            if transaction.source_account_id and transaction.dest_account_id:
                source = db.query(Account).filter(Account.id == transaction.source_account_id).first()
                dest = db.query(Account).filter(Account.id == transaction.dest_account_id).first()
                
                if source and dest:
                    # Decrease source (usually a bank account)
                    if source.type == AccountType.BANK or source.type == AccountType.CASH:
                        source.current_balance -= transaction.amount
                    
                    # Adjust destination
                    if dest.type == AccountType.CREDIT_CARD:
                        # Paying off credit card
                        dest.used_amount -= transaction.amount
                        if dest.used_amount < 0:
                            dest.used_amount = 0
                    elif dest.type == AccountType.BANK or dest.type == AccountType.CASH:
                        # Transfer to another bank/cash
                        dest.current_balance += transaction.amount
        
        db.commit()
    
    @staticmethod
    def revert_transaction(db: Session, transaction: Transaction):
        """Revert transaction effects from account balances"""
        if transaction.type == TransactionType.INCOME:
            if transaction.dest_account_id:
                account = db.query(Account).filter(Account.id == transaction.dest_account_id).first()
                if account and (account.type == AccountType.BANK or account.type == AccountType.CASH):
                    account.current_balance -= transaction.amount
        
        elif transaction.type == TransactionType.EXPENSE:
            if transaction.source_account_id:
                account = db.query(Account).filter(Account.id == transaction.source_account_id).first()
                if account:
                    if account.type == AccountType.BANK or account.type == AccountType.CASH:
                        account.current_balance += transaction.amount
                    elif account.type == AccountType.CREDIT_CARD:
                        account.used_amount -= transaction.amount
                        if account.used_amount < 0:
                            account.used_amount = 0
        
        elif transaction.type == TransactionType.TRANSFER:
            if transaction.source_account_id and transaction.dest_account_id:
                source = db.query(Account).filter(Account.id == transaction.source_account_id).first()
                dest = db.query(Account).filter(Account.id == transaction.dest_account_id).first()
                
                if source and dest:
                    # Revert source
                    if source.type == AccountType.BANK or source.type == AccountType.CASH:
                        source.current_balance += transaction.amount
                    
                    # Revert destination
                    if dest.type == AccountType.CREDIT_CARD:
                        dest.used_amount += transaction.amount
                    elif dest.type == AccountType.BANK or dest.type == AccountType.CASH:
                        dest.current_balance -= transaction.amount
        
        db.commit()
    
    @staticmethod
    def create_transaction(db: Session, transaction_data: dict, user_id: int) -> Transaction:
        """Create a new transaction and update balances"""
        transaction = Transaction(**transaction_data, user_id=user_id)
        db.add(transaction)
        db.flush()  # Get the ID
        
        TransactionService.apply_transaction(db, transaction)
        return transaction
    
    @staticmethod
    def update_transaction(db: Session, transaction: Transaction, update_data: dict):
        """Update transaction and recalculate balances"""
        # First revert the old transaction
        TransactionService.revert_transaction(db, transaction)
        
        # Update transaction fields
        for key, value in update_data.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        
        # Apply the new transaction
        TransactionService.apply_transaction(db, transaction)
    
    @staticmethod
    def delete_transaction(db: Session, transaction: Transaction):
        """Delete transaction and revert balances"""
        TransactionService.revert_transaction(db, transaction)
        db.delete(transaction)
        db.commit()
