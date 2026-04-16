from infrastructure.config.settings import DATABASE_URL
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base

DSN = DATABASE_URL
engine = sqlalchemy.create_engine(DSN)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()