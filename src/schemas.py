from pydantic import BaseModel, Field

class Season(BaseModel):
    league : str= Field(min_length=1)
    year : str = Field(min_length=1, max_length=20)

class NewSeason(Season):
    participating_teams: list= Field(min_length=1)

class UpdateSeason(Season):
    add_csv_file: list= Field(min_length=1)
    isComplete: bool= Field(default=False)
    overFilled: int = Field()
    remainingFixtures: list= Field(min_length=1)