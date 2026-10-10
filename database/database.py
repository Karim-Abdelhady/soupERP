from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.database_url)
Session = sessionmaker(bind = engine)
Base = declarative_base()

def get_db():
    db = Session()

    try:
        yield db
    finally:
        db.close()
