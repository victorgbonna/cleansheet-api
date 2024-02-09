from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from . import models, schemas

def get_seasons(db: Session, filterBy):
    if not filterBy:
        return db.query(models.Season).all()
    if filterBy=="incomplete":
        return db.query(models.Season).filter(models.Season.isComplete==False).all()
    if filterBy=="over-complete":
        return db.query(models.Season).filter(models.Season.overFilled==False).all()

def find_season_by_leagueXyear(db: Session, league:str, year:str):
    try:
        season=db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()
        return season
    except NoResultFound:
        return None

def save_season(db: Session, league:str, year:str, isComplete: bool, overFilled: int, remainingFixtures: list):
    new_season = models.Season(year=year, league=league, isComplete=isComplete, overFilled=overFilled, remainingFixtures=remainingFixtures)
    db.add(new_season)
    db.commit()
    db.refresh(new_season)
    return db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()

def update_season(db: Session, league:str, year:str, isComplete: bool, overFilled: int, remainingFixtures: list, csvFileLink:str):
    try:
        season_exists= db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()
        season_exists.csvFileLink=csvFileLink
        season_exists.isComplete =isComplete
        season_exists.overFilled =overFilled
        season_exists.remainingFixtures = remainingFixtures
        db.commit()
        return "done"
    except NoResultFound:
        return None

def update_season_url(db: Session, league:str, year:str, csvFileLink:str):
    try:
        season_exists= db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()
        season_exists.csvFileLink=csvFileLink
        db.commit()
        return "done"
    except NoResultFound:
        return None


