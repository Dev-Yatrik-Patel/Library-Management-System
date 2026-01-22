from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limiter import limiter

from app.core.database import Base, engine
from app.models import book,loan,role,user,refresh_token
from app.api import books, auth, users, loans

app = FastAPI(title = "Library Management System")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

Base.metadata.create_all(bind = engine)

app.include_router(books.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(loans.router)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

@app.get("/")
def home():
    return {"message": "Welcome to Library App"}

@app.get("/health")
def health_check():
    return { "message" : "Library app is running!"}