from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.rate_limiter import limiter

from app.core.database import Base, engine
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
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

@app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )

@app.exception_handler(AuthenticationError)
async def auth_exception_handler(
    request: Request,
    exc: AuthenticationError
):
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message}
    )

@app.exception_handler(AuthorizationError)
async def authorization_exception_handler(
    request: Request,
    exc: AuthorizationError
):
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message}
    )

@app.exception_handler(BookNotFound)
async def authorization_exception_handler(
    request: Request,
    exc: BookNotFound
):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message}
    )

@app.exception_handler(BookOutOfStock)
async def authorization_exception_handler(
    request: Request,
    exc: BookOutOfStock
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )

@app.exception_handler(AlreadyBorrowed)
async def authorization_exception_handler(
    request: Request,
    exc: AlreadyBorrowed
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )

@app.exception_handler(LoanNotFound)
async def authorization_exception_handler(
    request: Request,
    exc: LoanNotFound
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )

@app.exception_handler(InvalidLoanOperation)
async def authorization_exception_handler(
    request: Request,
    exc: InvalidLoanOperation
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )

@app.exception_handler(UserNotFound)
async def authorization_exception_handler(
    request: Request,
    exc: UserNotFound
):
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message}
    )
    
@app.exception_handler(UserLoanPending)
async def authorization_exception_handler(
    request: Request,
    exc: UserLoanPending
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )

@app.exception_handler(UserEmailAlreadyExists)
async def authorization_exception_handler(
    request: Request,
    exc: UserEmailAlreadyExists
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )


@app.get("/")
def home():
    return {"message": "Welcome to Library App"}

@app.get("/health")
def health_check():
    return { "message" : "Library app is running!"}