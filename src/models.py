from sqlalchemy import Column, Integer, String, Boolean, JSON
from .database import Base

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

    def __str__(self):
        return self.year+'-'+self.league