import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
PASSWORD_FOR_DB = os.getenv("PASSWORD_FOR_DB")