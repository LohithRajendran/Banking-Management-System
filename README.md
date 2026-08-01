# 🏦 Banking Management System — Full-Stack Enterprise Application

> Inspired by [LohithRajendran/Banking-Management-System](https://github.com/LohithRajendran/Banking-Management-System) — evolved from a console app into a production-grade full-stack system.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, HTML5, CSS3 (Vanilla), JavaScript (ES2023) |
| **Backend API** | Python 3.12, FastAPI, Django (ORM + Admin) |
| **Database** | PostgreSQL 16 |
| **Caching** | Redis 7 |
| **Task Queue** | Celery 5 (with Redis broker) |
| **Auth** | JWT (access + refresh tokens), bcrypt |
| **Testing** | pytest, pytest-asyncio, httpx |
| **Logging** | Python logging + structlog, rotating file handler |
| **Containerization** | Docker, Docker Compose |
| **Architecture** | Client-Server, RESTful API, MVC + Service Layer |

---

## 📁 Complete Project Structure

```
banking-management-system/
│
├── 📄 README.md                          ← Main project documentation
├── 📄 .gitignore
├── 📄 .env.example                       ← Environment variables template
├── 📄 docker-compose.yml                 ← Orchestrates all services
│
├── 🐍 backend/                           ← Python FastAPI + Django
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   ├── 📄 pyproject.toml                 ← Project metadata + pytest config
│   ├── 📄 manage.py                      ← Django management script
│   ├── 📄 alembic.ini                    ← DB migrations config
│   │
│   ├── 🗂️ config/                        ← App-wide configuration
│   │   ├── 📄 __init__.py
│   │   ├── 📄 settings.py               ← Django settings
│   │   ├── 📄 settings_fastapi.py       ← FastAPI / Pydantic settings
│   │   └── 📄 urls.py                   ← Django root URL config
│   │
│   ├── 🗂️ core/                          ← Shared utilities
│   │   ├── 📄 __init__.py
│   │   ├── 📄 database.py               ← SQLAlchemy engine + session
│   │   ├── 📄 redis_client.py           ← Redis connection
│   │   ├── 📄 security.py              ← JWT + password hashing
│   │   ├── 📄 logging_config.py        ← Logging setup
│   │   ├── 📄 exceptions.py            ← Custom exception classes
│   │   └── 📄 dependencies.py          ← FastAPI dependency injections
│   │
│   ├── 🗂️ models/                        ← SQLAlchemy ORM models
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py                  ← Declarative base
│   │   ├── 📄 user.py                  ← User model
│   │   ├── 📄 customer.py             ← Customer profile model
│   │   ├── 📄 account.py              ← Account model (savings/current)
│   │   ├── 📄 transaction.py          ← Transaction model
│   │   └── 📄 audit_log.py            ← Audit trail model
│   │
│   ├── 🗂️ schemas/                       ← Pydantic request/response schemas
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py                  ← Login, register, token schemas
│   │   ├── 📄 user.py                  ← User schemas
│   │   ├── 📄 customer.py             ← Customer schemas
│   │   ├── 📄 account.py              ← Account schemas
│   │   └── 📄 transaction.py          ← Transaction schemas
│   │
│   ├── 🗂️ repositories/                  ← Data access layer (CRUD)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base.py                  ← Generic CRUD base class
│   │   ├── 📄 user_repo.py            ← User CRUD operations
│   │   ├── 📄 customer_repo.py        ← Customer CRUD operations
│   │   ├── 📄 account_repo.py         ← Account CRUD operations
│   │   └── 📄 transaction_repo.py     ← Transaction CRUD operations
│   │
│   ├── 🗂️ services/                      ← Business logic layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth_service.py          ← Authentication & authorization
│   │   ├── 📄 account_service.py       ← Account business rules
│   │   ├── 📄 transaction_service.py   ← Transfer, deposit, withdraw logic
│   │   └── 📄 notification_service.py  ← Email notifications trigger
│   │
│   ├── 🗂️ api/                           ← FastAPI route handlers
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                  ← FastAPI app entry point
│   │   ├── 📄 router.py               ← Root API router
│   │   └── 🗂️ v1/
│   │       ├── 📄 __init__.py
│   │       ├── 📄 auth.py             ← POST /auth/login, /auth/register
│   │       ├── 📄 users.py            ← GET /users/me
│   │       ├── 📄 customers.py        ← GET/PUT /customers/me
│   │       ├── 📄 accounts.py         ← POST/GET /accounts
│   │       └── 📄 transactions.py     ← POST /transactions/*
│   │
│   ├── 🗂️ tasks/                         ← Celery async tasks
│   │   ├── 📄 __init__.py
│   │   ├── 📄 celery_app.py           ← Celery app instance
│   │   ├── 📄 email_tasks.py          ← Send transaction email notifications
│   │   ├── 📄 report_tasks.py         ← Generate monthly statements
│   │   └── 📄 interest_tasks.py       ← Calculate and apply interest
│   │
│   ├── 🗂️ migrations/                    ← Alembic DB migrations
│   │   ├── 📄 env.py
│   │   ├── 📄 script.py.mako
│   │   └── 🗂️ versions/
│   │       └── 📄 001_initial_schema.py
│   │
│   ├── 🗂️ django_admin/                  ← Django app for admin panel
│   │   ├── 📄 __init__.py
│   │   ├── 📄 admin.py                ← Django admin registrations
│   │   ├── 📄 apps.py
│   │   └── 📄 models.py              ← Django ORM models
│   │
│   └── 🗂️ tests/                         ← pytest test suite
│       ├── 📄 __init__.py
│       ├── 📄 conftest.py             ← Fixtures
│       ├── 🗂️ unit/
│       │   └── 📄 test_security.py
│       └── 🗂️ integration/
│           └── 📄 test_auth_api.py
│
├── ⚛️ frontend/                           ← React + HTML/CSS/JS
│   ├── 📄 Dockerfile
│   ├── 📄 package.json
│   ├── 📄 vite.config.js              ← Vite bundler config
│   ├── 📄 index.html                  ← Root HTML shell
│   │
│   └── 🗂️ src/
│       ├── 📄 main.jsx                ← React entry point
│       ├── 📄 App.jsx                 ← Root component + routing
│       ├── 📄 index.css              ← Global CSS design system
│       │
│       ├── 🗂️ api/
│       │   └── 📄 axios.js           ← Axios instance + interceptors
│       │
│       ├── 🗂️ context/
│       │   └── 📄 AuthContext.jsx    ← Auth state management
│       │
│       ├── 🗂️ components/
│       │   └── 🗂️ common/
│       │       └── 📄 ProtectedRoute.jsx
│       │
│       └── 🗂️ pages/
│           ├── 📄 LoginPage.jsx
│           ├── 📄 RegisterPage.jsx
│           └── 📄 DashboardPage.jsx
│
└── 🗂️ nginx/
    ├── 📄 Dockerfile
    └── 📄 nginx.conf                  ← Reverse proxy routing
```

---

## 🔗 Connection Architecture

```
Browser (React Frontend :3000)
    │
    │ HTTP Requests
    ▼
[Nginx Reverse Proxy :80]
    │
    ├── /api/* ──────────────► [FastAPI Backend :8000]
    │                                │
    │                                ├── Auth (JWT)
    │                                ├── Business Services
    │                                ├── Repository Layer
    │                                ├── SQLAlchemy ──► [PostgreSQL :5432]
    │                                ├── Redis ────────► [Redis :6379]
    │                                └── Celery Tasks ─► [Celery Worker]
    │
    └── /* ──────────────────► [React Frontend :3000]
```

---

## 🛠️ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/LohithRajendran/Full-stack-Banking-Management-System.git
cd Full-stack-Banking-Management-System

# 2. Copy environment template
cp .env.example .env

# 3. Start all services using Docker Compose
docker-compose up --build

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Access application
# Frontend:     http://localhost
# API Specs:    http://localhost/api/docs
# Django Admin: http://localhost/django-admin
```
