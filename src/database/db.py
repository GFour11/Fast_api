import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE = os.environ.get('DB')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')


DB = f'postgresql+psycopg2://{DATABASE}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DB)

SESSION = sessionmaker(autocommit = False, autoflush= False, bind= engine)

def get_db():
    """Connection to database"""
    db = SESSION()
    try:
        yield db
    finally:
        db.close()