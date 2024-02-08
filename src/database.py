from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import DATABASE_URL

# print(DATABASE_URL)
# SQLACHEMY_URL= "sqlite:///./seasons.db"
SQLACHEMY_URL= DATABASE_URL
engine= create_engine(
    SQLACHEMY_URL
    # , connect_args={'check_same_thread':False}   
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()