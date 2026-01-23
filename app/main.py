from fastapi import FastAPI, Request,HTTPException
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limiter import limiter

from app.core.database import Base, engine
from app.core.response import error_response
from app.models import book,loan,role,user,refresh_token,audit_log
from app.api import books, auth, users, loans

from app.exceptions.base import AppException
from app.exceptions.auth import AuthenticationError, AuthorizationError
from app.exceptions.book import BookNotFound,BookOutOfStock
from app.exceptions.loan import AlreadyBorrowed,LoanNotFound,InvalidLoanOperation
from app.exceptions.user import UserNotFound,UserLoanPending,UserEmailAlreadyExists


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
    return error_response(
        message="Too many requests. Please try again later.",
        error_code="TOO_MANY_REQUESTS",
        status_code=429
    )

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return error_response(
        message=exc.message,
        error_code=exc.error_code,
        status_code=exc.status_code
    )

@app.exception_handler(HTTPException)
async def app_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        message=exc.detail,
        error_code="HTTP_ERROR",
        status_code=exc.status_code
    )

@app.get("/")
def home():
    return {"message": "Welcome to Library App"}

@app.get("/health")
def health_check():
    return { "message" : "Library app is running!"}