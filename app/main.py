from fastapi import FastAPI
from app.core.database import Base, engine

from app.models import book,loan,role,user
from app.api import books, auth, users

app = FastAPI(title = "Library Management System")

Base.metadata.create_all(bind = engine)

app.include_router(books.router)
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def home():
    return {"message": "Welcome to Library App"}

@app.get("/health")
def health_check():
    return { "message" : "Library app is running!"}

