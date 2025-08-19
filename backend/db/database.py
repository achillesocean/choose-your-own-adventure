from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

from sqlalchemy.orm import DeclarativeBase

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, bind=engine, autocommit=False)

# Base = declarative_base()
class Base(DeclarativeBase):
  pass

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()  

def create_tables():
  Base.metadata.create_all(bind=engine)