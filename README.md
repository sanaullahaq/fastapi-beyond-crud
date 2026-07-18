# FastAPI Beyond CRUD

A book review API with authentication, Celery background tasks, rate limiting, and a comprehensive test suite.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLModel (SQLAlchemy 2.0 ORM)
- **Auth**: JWT (access + refresh tokens), email verification, password reset
- **Background Tasks**: Celery + Redis
- **Rate Limiting**: SlowAPI + Redis
- **Migrations**: Alembic
- **Testing**: pytest, pytest-asyncio, httpx

## Setup

```bash
python3 -m venv env && source env/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bookly
JWT_SECRET = 
JWT_ALGORITHM = 
ACCESS_TOKEN_EXPIRY_SECONDS = 3600
REFRESH_TOKEN_EXPIRY_DAYS = 2
REDIS_URL = redis://localhost:6379/0
JTI_EXPIRY_SECONDS = 3600
DB_ECHO = False

MAIL_USERNAME=example@mail.com
MAIL_PASSWORD=xxxxxxxxxxxxxxxx
# Gmail blocks plain password SMTP auth. You need an App Password:
# Go to your Google Account → Security
# Enable 2-Step Verification (mandatory prerequisite — App Passwords won't show up without it)
# Go to Security → 2-Step Verification → App passwords (or search "App passwords" in your Google Account search bar)
# Create one — name it something like fastapi-beyond-crud
# Google gives you a 16-character password like abcd efgh ijkl mnop — copy it without spaces: abcdefghijklmnop

MAIL_FROM=example@mail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Bookly
DOMAIN=localhost:8000
```

Run migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
fastapi dev src/
```

## Run Tests

```bash
pytest tests/ -v
```

Requires a `bookly_test` database:

```sql
CREATE DATABASE bookly_test;
```

## Project Structure

```
src/
├── auth/       # User signup, login, verification, password reset
├── books/      # Book CRUD
├── reviews/    # Review CRUD with ownership checks
├── tags/       # Tag CRUD, many-to-many with books
├── db/         # Engine, session, models, Redis client
├── errors.py   # Custom exceptions + handlers
├── middleware.py   # CORS, logging, rate limiter
└── celery_tasks.py # Async email tasks

tests/
├── conftest.py     # Shared fixtures (engine, session, client, auth)
├── test_auth/      # 30 tests
├── test_books/     # 32 tests
├── test_reviews/   # 19 tests
└── test_tags/      # 23 tests
```

## API Endpoints

| Prefix | Description |
|--------|-------------|
| `/api/v1/auth` | Signup, login, logout, refresh, verify, password reset |
| `/api/v1/books` | Book CRUD |
| `/api/v1/reviews` | Review CRUD (admin list, user add/delete own) |
| `/api/v1/tags` | Tag CRUD, add tags to books |

Docs at `/api/v1/docs` (Swagger) and `/api/v1/redoc`.
