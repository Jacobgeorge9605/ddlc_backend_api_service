# ddlc_backend_api_service

FastAPI backend service with Stage and Production environment support.

---

## Project Structure

```
ddlc_backend_api_service/
│
├── main.py                        # Entry point — starts the uvicorn server
├── requirements.txt               # All Python dependencies
├── .env.stage                     # Stage environment variables
├── .env.prod                      # Production environment variables
├── .gitignore
├── venv/                          # Virtual environment (not committed)
│
└── app/
    ├── main.py                    # FastAPI app factory (app instance lives here)
    │
    ├── api/                       # All HTTP route definitions
    │   └── v1/
    │       ├── __init__.py        # Registers all v1 routers under /api/v1
    │       └── routes/
    │           ├── __init__.py
    │           └── health.py      # GET /api/v1/health  ← example route file
    │
    ├── core/                      # App-wide configuration and setup
    │   ├── config.py              # Environment-based settings (reads .env file)
    │   └── middleware.py          # CORS and other middleware registration
    │
    ├── models/                    # Database table/collection definitions
    ├── schemas/                   # Pydantic request and response shapes
    ├── services/                  # Business logic (called by routes)
    └── db/                        # Database session and connection setup
```

---

## Where to Write Your Code

### Adding a New API Endpoint

1. Create a new file in `app/api/v1/routes/`

   **Example:** `app/api/v1/routes/users.py`
   ```python
   from fastapi import APIRouter

   router = APIRouter()

   @router.get("/users", tags=["Users"])
   async def get_users():
       return [{"id": 1, "name": "Jacob"}]
   ```

2. Register it in `app/api/v1/__init__.py`
   ```python
   from app.api.v1.routes import health, users   # add users

   router = APIRouter(prefix="/api/v1")
   router.include_router(health.router)
   router.include_router(users.router)            # add this line
   ```

---

### Adding a Database Model

Write in `app/models/`

**Example:** `app/models/user.py`
```python
# If using SQLAlchemy:
from sqlalchemy import Column, Integer, String
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
```

---

### Adding a Request / Response Schema

Write in `app/schemas/`

**Example:** `app/schemas/user.py`
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
```

Use in your route:
```python
from app.schemas.user import UserCreate, UserResponse

@router.post("/users", response_model=UserResponse)
async def create_user(payload: UserCreate):
    ...
```

---

### Adding Business Logic

Write in `app/services/`

Keep routes thin — put all logic here.

**Example:** `app/services/user_service.py`
```python
from app.schemas.user import UserCreate

async def create_user(data: UserCreate):
    # talk to DB, send emails, call external APIs, etc.
    return {"id": 1, **data.model_dump()}
```

Call from your route:
```python
from app.services import user_service

@router.post("/users")
async def create_user(payload: UserCreate):
    return await user_service.create_user(payload)
```

---

### Database Connection Setup

Write in `app/db/`

**Example:** `app/db/session.py`
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
```

---

### Adding / Changing Config Variables

Edit `app/core/config.py` — add your variable to the `Settings` class:
```python
class Settings(BaseSettings):
    MY_NEW_VAR: str = "default"
```

Then add the value to `.env.stage` and `.env.prod`:
```
MY_NEW_VAR=some-value
```

Access it anywhere:
```python
from app.core.config import get_settings
settings = get_settings()
print(settings.MY_NEW_VAR)
```

---

### Adding Middleware

Edit `app/core/middleware.py`:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

def register_middleware(app: FastAPI) -> None:
    app.add_middleware(CORSMiddleware, ...)
    app.add_middleware(HTTPSRedirectMiddleware)   # add new middleware here
```

---

## Environment Files

| Variable | Stage | Prod |
|---|---|---|
| `ENV` | `stage` | `prod` |
| `DEBUG` | `true` | `false` |
| `PORT` | `7000` | `7000` |
| `SECRET_KEY` | change me | change me |
| `REDIS_HOST` | `localhost` | `redis` |
| `DATABASE_URL` | (fill in) | (fill in) |
| `ALLOWED_ORIGINS` | localhost URLs | your domain |

> **Note:** Never commit `.env.prod` — it contains secrets. It is already in `.gitignore`.

---

## Running the Service

### Setup (first time)
```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Stage (hot-reload enabled)
```bash
ENV_FILE=.env.stage venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 7000 --reload
```

### Production
```bash
ENV_FILE=.env.prod venv/bin/python main.py
```

---

## Available Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Health check — returns app name, version, env |
| GET | `/docs` | Swagger UI (stage only) |
| GET | `/redoc` | ReDoc UI (stage only) |

---

## Quick Reference — What Goes Where

| What you are building | Where to put it |
|---|---|
| New API route / endpoint | `app/api/v1/routes/` |
| Register a new router | `app/api/v1/__init__.py` |
| Database table / model | `app/models/` |
| Request / response shape | `app/schemas/` |
| Business / processing logic | `app/services/` |
| DB connection / session | `app/db/` |
| Environment variable | `app/core/config.py` + `.env.*` |
| CORS / middleware | `app/core/middleware.py` |
| App startup / shutdown events | `app/main.py` |
