from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

load_dotenv()
db_url = os.getenv('DB_URL')
engine = create_engine(db_url, echo=True)
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
