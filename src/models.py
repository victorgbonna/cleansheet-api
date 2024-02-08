from sqlalchemy import Column, Integer, String, Boolean, JSON
from .database import Base

class Season(Base):
    __tablename__ = "seasons"

    id = Column(Integer, primary_key=True, index=True)
    league = Column(String, index=True)
    year = Column(String, index=True)
    isComplete= Column(Boolean, default=True)
    overFilled= Column(Integer, default=0)
    remainingFixtures = Column(JSON, default=[])

    def __str__(self):
        return self.year+'-'+self.league