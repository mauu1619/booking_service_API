# Booking Service API 

REST API for booking service on FastApi.

**Live Demo:** https://booking-api.mau1619.website

**Swagger UI(API docs):** https://booking-api.mau1619.website/docs

## Technology stack

- **Python 3.12**
- **FastAPI**
- **PostgreSQL**
- **Redis**
- **Taskiq**
- **SQLAlchemy 2.0 (async)**
- **SQLModel**
- **Alembic**
- **Pydantic v2**
- **JWT authentication**
- **Docker**
- **GitHub Actions**

## Project Structure

```
app/
├── api
│   ├── deps.py             # FastAPI dependencies
│   └── routers
│       ├── auth.py         # Authentication        
│       ├── bookings.py     # Bookings
│       └── rooms.py        # Rooms
├── logs
│   ├── app.log             # App's logs                
│   └── error.log           # Errors' logs
├── core
│   ├── config.py           # Configuration
│   ├── logger.py           # Logger setup
│   └── security.py         # JWT and password hashing
├── db
│   ├── crud.py             # Database interaction functions
│   ├── redis.py            # Redis connection
│   └── session.py          # Database connection
├── models
│   ├── bookings.py         # SQLModel bookings models and schemas
│   ├── rooms.py            # SQLModel rooms model and schemas
│   └── users.py            # SQLModel users model and schemas
├── scripts                 
│   └── create_admin.py     # Create admin script
├── main.py                 # Entry point
├── start.sh                # Start script
└── tasks.py                # Async worker 
```

## Quick Start

### With Docker (recommended)

```bash
# Clone the repository
git clone https://github.com/mauu1619/booking_service_API.git
cd booking_service_API

# Create .env file
cp .env.example .env

# Run containers
docker compose up --build
```

API will be available at: http://localhost:8000

Swagger UI: http://localhost:8000/docs

### Locally (without Docker)

### *with pip (recommended)*

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate # Linux/Mac
venv/Scripts/activate # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set DATABASE URL and REDIS URL for local PostqreSQL and Redis

# Apply migrations
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

### *with uv (faster)*

```bash
# install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh # Linux/Mac
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" # Windows

# Install dependencies and create .venv
uv sync --frozen 

cp .env.example .env

uv run alembic upgrade head

uv run uvicorn app.main:app --reload
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------| 
| POST | /auth/register | Register user | Public |
| POST | /auth/login | Login (JWT Tokens) | Public |
| POST | /auth/refresh | Update tokens | Public |
| POST | /auth/logout | Delete refresh | Public |
| GET | /auth/me | Return a current user | Authenticated |
| DELETE | /auth/{id} | Delete user (inactive) | Admin |

### Rooms 

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /rooms | List rooms (Pagination, filtering) | Public |
| GET | /rooms/{id} | Get room details | Public |
| POST | /rooms | Create a room | Admin |
| PATCH | /rooms/{id} | Edit room | Admin |   
| DELETE | /rooms/{id} | Delete room | Admin |

### Bookings

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | /bookings | List my bookings | Authenticated |
| POST | /bookings | Create booking and send email on background | Authenticated |
| DELETE | /bookings/{id} | Cancel booking | Owner, Admin |

## Request Examples

### Registration 

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user@example.com", "password": "secret123"}'
```

### List of rooms

```bash
curl http://localhost:8000/rooms?limit=10&offset=0
```

### Creating a booking

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"room_id": 1, "date_from": "2026-06-20", "date_to": "2026-06-24"}'
```

## Testing

### Inside Docker 

```bash
docker compose exec app uv run pytest
```

### Locally

```bash
pytest
```

## Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------| 
| DATABASE_URL | PostgreSQL connection URL | postgresql+asyncpg://${DB_USER}:${DB_PASS}@db:5432/${DB_NAME} |
| REDIS_URL | Redis connection URL | redis://redis:6379 |
| DB_USER | Database user name | postgres |
| DB_NAME | Database name | bookings_db |
| DB_PASS | Database user's password | postgres |
| SECRET_KEY | Secret key for JWT | your-secret-key(hex) |
| ALGORITHM | Algorithm for JWT | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime (minutes) | 15 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime (days) | 7 |
| DUMMY_HASH | Placeholder hash used for fallback scenarios (e.g. user not found) | your-dummy-hash |
| SUPERUSER_EMAIL | Default admin email | admin@example.com |
| SUPERUSER_PASSWORD | Default admin password | admin1619 |
| MAIL_SERVER | SMTP server used for sending email | your.smtp.server |
| MAIL_PORT | SMTP server port | 2525 |
| MAIL_USERNAME | SMTP username | your_username |
| MAIL_PASSWORD | SMTP password | password123 |
| ENV | Application environment (affects logging) | dev / prod | 
| UID | User ID used inside Docker | 1000 |
| GID | Group ID used inside Docker | 1000 |

> Always override environment variables via .env file or deployment evironment.

> Get UID and GID on linux:
> ```bash
> id -u # UID
> id -g # GID
> ```
> On Windows you can leave the default values (1000) or use WSL

> For local dev change database host on localhost
