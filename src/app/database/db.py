import os
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine
)
from databases import Database

load_dotenv()

USERNAME = os.getenv("DATABASE_USERNAME")
PASSWORD = os.getenv("DATABASE_PASSWORD")
HOST = os.getenv("DATABASE_HOST")
PORT = os.getenv("DATABASE_PORT")
DATABASE = os.getenv("DATABASE")

DATABASE_URL = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}" 

# Generating database models according to the URL passed
engine = create_engine(DATABASE_URL)

# databases query builder using databases library
database = Database(DATABASE_URL)