from fastapi import FastAPI
from . import crud, models
# from .models import  Season
from .database import engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from .routers import season_routes

models.Base.metadata.create_all(bind=engine)

app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing purposes, modify as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    try:
        db=SessionLocal()
        yield db
    finally:
        db.rollback()
        db.close()



app.include_router(season_routes.router, prefix="/seasons", tags=["Seasons"])

