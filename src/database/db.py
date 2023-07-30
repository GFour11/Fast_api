from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB = 'postgresql+psycopg2://postgres:567234@195.201.150.230:5433/fast_api_GFour'

engine = create_engine(DB)

SESSION = sessionmaker(autocommit = False, autoflush= False, bind= engine)

def get_db():
    db = SESSION()
    try:
        yield db
    finally:
        db.close()