# 💰 Expense Manager - Personal Finance Tracker

A comprehensive, production-ready expense management web application built with **FastAPI**, **Jinja2**, and **TailwindCSS**.

## ✨ Features

### 🔐 User Management
- **Admin Dashboard**: Create and manage users, system statistics
- **Role-Based Access**: Admin and Standard user roles
- **Secure Authentication**: Session-based with bcrypt password hashing
- **Mandatory Password Change**: First-time login security

### 💳 Account Management
- **Bank Accounts**: Track multiple bank accounts with current balances
- **Credit Cards**: Monitor credit limits, used amounts, and payment due dates
- **Cash Wallet**: Simple cash tracking
- **Visual Indicators**: Utilization bars for credit cards

### 📊 Transaction Tracking
- **Income**: Record salary, bonuses, refunds
- **Expenses**: Track spending with category tagging
- **Transfers**: Move money between accounts or pay credit card bills
- **Receipt Upload**: Attach receipt images to transactions
- **Search & Filter**: Find transactions by description, date, category, or account

### 📈 Budgeting & Analytics
- **Monthly Budgets**: Set spending limits per category
- **Budget Alerts**: Visual warnings when exceeding budgets
- **Dashboard Charts**:
  - Expense breakdown by category (pie chart)
  - Weekly spending trend (line chart)
  - Income vs. Expense comparison (bar chart)
  - Payment mode analysis
- **Net Worth Calculation**: Total assets minus liabilities
- **Upcoming Payments**: Credit card due date reminders

### 📁 Export & Reporting
- **CSV Export**: Download transaction history
- **Excel Export**: Formatted spreadsheets with all details

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first, works on all devices
- **Beautiful Gradients**: Eye-catching color schemes
- **Google Icons**: Material Symbols throughout
- **Smooth Animations**: Micro-interactions for better UX
- **TailwindCSS**: Modern, utility-first styling

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- UV (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   cd expense_manager_v2
   ```

2. **Install dependencies**:
   ```bash
   uv add fastapi uvicorn[standard] jinja2 sqlalchemy python-multipart python-dotenv bcrypt itsdangerous psycopg2-binary pandas openpyxl aiosqlite
   ```

3. **Configure environment** (optional - defaults work for development):
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` if needed:
   ```
   DATABASE_URL=sqlite:///./expense_manager.db
   SECRET_KEY=your-secret-key-here
   UPLOAD_DIR=uploads
   ```

4. **Run the application**:
   ```bash
   uv run uvicorn main:app --reload
   ```

5. **Access the application**:
   Open your browser to: http://localhost:8000

### Default Login Credentials

- **User ID**: `adminExpense`
- **Password**: `adminExpense`

> ⚠️ You will be prompted to change the password on first login.

## 📱 Using the Application

### For Admins

1. **Login** with admin credentials
2. **Change password** (required on first login)
3. **Create users** from the Admin Dashboard
4. **Manage users**: Enable, disable, or delete user accounts

### For Standard Users

1. **Login** with assigned credentials
2. **Change password** (required on first login)
3. **Add accounts**: Bank accounts, credit cards, or cash wallet
4. **Record transactions**:
   - Income: Add salary or other income sources
   - Expenses: Track daily spending
   - Transfers: Pay credit card bills or move money
5. **Set budgets**: Create monthly spending limits per category
6. **Monitor finances**: View dashboard charts and alerts
7. **Export data**: Download transaction history as CSV or Excel

## 🗂️ Project Structure

```
expense_manager_v2/
├── app/
│   ├── config.py           # Environment configuration
│   ├── database.py         # SQLAlchemy setup
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication utilities
│   ├── init_db.py          # Database initialization
│   ├── routes/             # API route handlers
│   ├── services/           # Business logic layer
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS/JS assets
├── main.py                 # FastAPI application
├── .env                    # Environment variables (gitignored)
└── pyproject.toml          # Project dependencies
```

## 🔧 Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLAlchemy ORM (SQLite/PostgreSQL)
- **Frontend**: Jinja2 Templates + TailwindCSS
- **Icons**: Google Material Symbols
- **Charts**: Chart.js
- **Authentication**: Session-based with bcrypt
- **Export**: Pandas + OpenPyXL

## 🗄️ Database

The application automatically creates all necessary tables on first run, including:

- **Users**: Authentication and profiles
- **Accounts**: Bank accounts, credit cards, cash
- **Categories**: Income and expense categories (system + custom)
- **Transactions**: All financial transactions
- **Budgets**: Monthly spending limits

### Switching to PostgreSQL

Update `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/expense_manager
```

## 🛡️ Security Features

- ✅ **Password Hashing**: Bcrypt for secure password storage
- ✅ **Session Management**: Secure cookie-based sessions
- ✅ **Forced Password Change**: On first login for all users
- ✅ **Role-Based Access**: Admin vs. User permissions
- ✅ **SQL Injection Protection**: SQLAlchemy ORM
- ✅ **Environment Secrets**: Sensitive data in `.env` (gitignored)

## 📊 Database Models

### User
- `user_id` (username), `password_hash`, `role` (admin/user)
- `name`, `email`, `is_active`, `must_change_password`

### Account
- Types: `bank`, `credit_card`, `cash`
- Banks: `current_balance`, `account_number`
- Credit Cards: `total_limit`, `used_amount`, `due_date`

### Transaction
- Types: `income`, `expense`, `transfer`
- Links to categories and accounts
- Automatic balance updates

### Budget
- Monthly spending limits per category
- Real-time spending comparison

## 🎯 Key Features

| Feature | Status |
|---------|--------|
| User Authentication | ✅ |
| Admin User Management | ✅ |
| Bank Account Tracking | ✅ |
| Credit Card Management | ✅ |
| Transaction Recording | ✅ |
| Receipt Upload | ✅ |
| Budget Setting | ✅ |
| Budget Alerts | ✅ |
| Dashboard Analytics | ✅ |
| Chart Visualizations | ✅ |
| CSV/Excel Export | ✅ |
| Mobile Responsive | ✅ |
| Category Management | ✅ |

## 📝 License

This project is open-source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📧 Support

For issues or questions, please open an issue on the repository.

---

**Built with ❤️ using FastAPI, TailwindCSS, and modern web technologies**
