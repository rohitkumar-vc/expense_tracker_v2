from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models import User, Category, UserRole, CategoryType
from app.auth import hash_password


def create_default_admin(db: Session):
    """Create default admin user if not exists"""
    admin = db.query(User).filter(User.user_id == "adminExpense").first()
    
    if not admin:
        admin = User(
            user_id="adminExpense",
            password_hash=hash_password("adminExpense"),
            role=UserRole.ADMIN,
            name="Administrator",
            email="admin@expense.local",
            is_active=True,
            must_change_password=True
        )
        db.add(admin)
        db.commit()
        print("✓ Default admin user created (adminExpense / adminExpense)")
    else:
        print("✓ Admin user already exists")


def create_default_categories(db: Session):
    """Create default system categories for all users"""
    default_income_categories = [
        "Salary",
        "Bonus",
        "Refund",
        "Investment Returns",
        "Gift Received",
        "Other Income"
    ]
    
    default_expense_categories = [
        "Food & Dining",
        "Groceries",
        "Transportation",
        "Rent",
        "Utilities",
        "Healthcare",
        "Entertainment",
        "Shopping",
        "Education",
        "Insurance",
        "Travel",
        "Other Expense"
    ]
    
    # Get admin user
    admin = db.query(User).filter(User.user_id == "adminExpense").first()
    
    if admin:
        # Check if categories already exist
        existing = db.query(Category).filter(
            Category.user_id == admin.id,
            Category.is_system == True
        ).count()
        
        if existing == 0:
            # Create income categories
            for cat_name in default_income_categories:
                category = Category(
                    user_id=admin.id,
                    name=cat_name,
                    type=CategoryType.INCOME,
                    is_system=True
                )
                db.add(category)
            
            # Create expense categories
            for cat_name in default_expense_categories:
                category = Category(
                    user_id=admin.id,
                    name=cat_name,
                    type=CategoryType.EXPENSE,
                    is_system=True
                )
                db.add(category)
            
            db.commit()
            print("✓ Default categories created")
        else:
            print("✓ Default categories already exist")


def init_database():
    """Initialize database: create tables and seed default data"""
    print("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Create default data
    db = SessionLocal()
    try:
        create_default_admin(db)
        create_default_categories(db)
        print("\n✅ Database initialization complete!")
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
