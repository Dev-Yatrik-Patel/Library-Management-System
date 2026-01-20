from fastapi import FastAPI
from app.core.database import Base, engine

from app.models import book,loan,role,user

app = FastAPI(title = "Library Management System")

Base.metadata.create_all(bind = engine)

@app.get("/health")
def health_check():
    return { "message" : "Library app is running!"}