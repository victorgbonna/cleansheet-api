from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from . import models, schemas

def get_seasons(db: Session, filterBy):
    if not filterBy:
        seasons=db.query(models.Season).all() 
    elif filterBy=="incomplete":
        seasons= db.query(models.Season).filter(models.Season.isComplete==False).all()
    elif filterBy=="over-complete":
        seasons=db.query(models.Season).filter(models.Season.overFilled==False).all()
    seasons_exc_fixtures=[{column.name: getattr(row, column.name) for column in row.__table__.columns if column.name!="fixtures"} for row in seasons]
    # seasons_exc_fixtures=[{k: v for k, v in row.items() if k != 'fixtures'} for row in seasons_exc_fixtures]
    return seasons_exc_fixtures
def find_season_by_leagueXyear(db: Session, league:str, year:str):
    try:
        season=db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()
        return season
    except NoResultFound:
        return None

def save_season(db: Session, league:str, year:str, isComplete: bool, overFilled: int, remainingFixtures: list, fixtures: list):
    print(len(fixtures))
    new_season = models.Season(year=year, league=league, isComplete=isComplete, overFilled=overFilled, remainingFixtures=remainingFixtures, fixtures=fixtures)
    db.add(new_season)
    db.commit()
    db.refresh(new_season)
    return db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()

def update_season_visits(db: Session, league:str, year:str):
    try:
        season_exists= db.query(models.Season).filter(models.Season.league == league, models.Season.year == year).first()
        if season_exists.noOfVisits is not None:
            season_exists.noOfVisits+=1
        else:
            season_exists.noOfVisits=1
        db.commit()
        return "done"
    except NoResultFound:
        return None


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


