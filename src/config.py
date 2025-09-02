import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("CLEANSHEET_API_DB_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

print(DATABASE_URL)