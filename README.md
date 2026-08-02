# 🏦 SecureBank — Full-Stack Banking Application

A complete banking application with **React** frontend and **Django** backend.

## ✨ Features
- 🔐 Signup & Login with JWT tokens
- 🏦 Create Bank Account (with ₹1000 welcome bonus!)
- 💸 Bank Transfer — send money using account number
- ⚡ Web ID Transfer — send money using a short unique ID (like UPI)
- 📊 Dashboard — view balance, account info, recent transactions
- 📜 Transaction History — filter by type, search by name

---

## 🛠️ Tech Stack

| Layer | Technology | What it does |
|-------|-----------|-------------|
| Frontend | React + Vite | User interface |
| Backend | Django + DRF | API server |
| Database | SQLite (default) / PostgreSQL | Data storage |
| Cache | In-memory / Redis (optional) | Fast caching |
| Auth | JWT Tokens | Secure login |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- pip and npm available

---

### STEP 1: Setup the Backend (Django)

Open a terminal and run:

```bash
# Go to the backend folder
cd backend

# Create a virtual environment (a clean Python environment for this project)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all Python packages
pip install -r requirements.txt

# Create your .env file (copy the example)
copy .env.example .env   # Windows
# or: cp .env.example .env  (Mac/Linux)

# Create the database tables
python manage.py makemigrations banking
python manage.py migrate

# (Optional) Create an admin user to access /admin/
python manage.py createsuperuser

# Start the Django server
python manage.py runserver
```

✅ Django is now running at: **http://localhost:8000**
✅ Admin panel: **http://localhost:8000/admin/**

---

### STEP 2: Setup the Frontend (React)

Open a **second terminal** and run:

```bash
# Go to the frontend folder
cd frontend

# Install all JavaScript packages
npm install

# Start the React development server
npm run dev
```

✅ React is now running at: **http://localhost:5173**

---

### STEP 3: Use the App

1. Open **http://localhost:5173** in your browser
2. Click **"Create one for free"** to sign up
3. After signup, click **"Open Bank Account"** to create your bank account
4. You'll receive a **₹1000 welcome bonus** 🎉
5. Note your **Account Number** and **Web ID** from the dashboard
6. Open a second browser (or incognito) and sign up as another user
7. Try sending money between the two accounts!

---

## 📂 Project Structure

```
banking-app/
│
├── backend/                      ← Django Server
│   ├── manage.py                 ← Run Django commands here
│   ├── requirements.txt          ← Python packages to install
│   ├── .env.example              ← Copy to .env and fill in
│   │
│   ├── config/
│   │   ├── settings.py           ← All Django configuration
│   │   └── urls.py               ← Main URL router
│   │
│   └── banking/                  ← Main app
│       ├── models.py             ← Database tables (User, BankAccount, Transaction)
│       ├── views.py              ← API endpoints (signup, login, transfer, etc.)
│       ├── serializers.py        ← Convert data to/from JSON
│       ├── urls.py               ← Banking URL routes
│       ├── utils.py              ← Helper functions (transfer logic, caching)
│       └── admin.py              ← Register models in admin panel
│
└── frontend/                     ← React App
    ├── package.json              ← JavaScript packages to install
    ├── vite.config.js            ← Build tool config
    ├── index.html                ← HTML entry point
    │
    └── src/
        ├── main.jsx              ← React entry point
        ├── App.jsx               ← Routing setup
        ├── index.css             ← Global styles & design system
        │
        ├── api/
        │   └── axios.js          ← HTTP client (auto-adds JWT token)
        │
        ├── context/
        │   └── AuthContext.jsx   ← Login/logout state management
        │
        ├── components/
        │   ├── Navbar.jsx        ← Navigation bar
        │   └── ProtectedRoute.jsx ← Redirect to login if not logged in
        │
        └── pages/
            ├── Login.jsx         ← Login form
            ├── Signup.jsx        ← Registration form
            ├── CreateAccount.jsx ← Open bank account
            ├── Dashboard.jsx     ← Home screen with balance
            ├── Transfer.jsx      ← Send money (bank or Web ID)
            └── History.jsx       ← Transaction history
```

---

## 🔌 API Endpoints

All endpoints start with `http://localhost:8000/api/`

| Method | URL | What it does | Auth? |
|--------|-----|-------------|-------|
| POST | `/signup/` | Create new user | ❌ |
| POST | `/login/` | Login, get JWT token | ❌ |
| POST | `/token/refresh/` | Refresh expired token | ❌ |
| POST | `/create-account/` | Create bank account | ✅ |
| GET | `/dashboard/` | Get balance & account info | ✅ |
| POST | `/transfer/bank/` | Transfer by account number | ✅ |
| POST | `/transfer/webid/` | Transfer by Web ID | ✅ |
| GET | `/transactions/` | Transaction history | ✅ |
| GET | `/lookup/webid/<id>/` | Find user by Web ID | ✅ |
| GET | `/lookup/account/<no>/` | Find account by number | ✅ |

---

## 🔧 Optional: Enable PostgreSQL

1. Install PostgreSQL on your PC
2. Create a database: `CREATE DATABASE banking_db;`
3. Edit `backend/.env`:
   ```
   USE_POSTGRESQL=True
   DB_NAME=banking_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
4. Run: `python manage.py migrate`

---

## 🔧 Optional: Enable Redis Cache

1. Install Redis on your PC
2. Edit `backend/.env`:
   ```
   USE_REDIS=True
   REDIS_URL=redis://127.0.0.1:6379/1
   ```
3. Restart Django server

---

## 📖 Key Concepts (Simple Explanation)

- **JWT Token** → Like a hotel key card. Login gives you a token. Show it with every request to prove who you are.
- **REST API** → React and Django talk to each other by sending JSON data over HTTP.
- **Django ORM** → Write Python code (models) instead of SQL to work with the database.
- **React Context** → A way to share data (like "who is logged in") with all components without passing it through props.
- **Axios Interceptor** → Runs code before every API call (we use it to automatically add the JWT token).
