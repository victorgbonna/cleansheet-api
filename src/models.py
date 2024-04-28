from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from .database import Base
import datetime

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    league = Column(String)
    year = Column(String)
    isComplete= Column(Boolean, default=True)
    csvFileLink= Column(String, default='')
    cloudPublicId= Column(String, default='')
    overFilled= Column(Integer, default=0)
    remainingFixtures = Column(JSON, default=[])
    fixtures = Column(JSON, default=[])
    noOfVisits= Column(Integer, default=1)
    created_at = Column(
        DateTime,
        default=datetime.datetime.now,
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    def __str__(self):
        return self.year+'-'+self.league