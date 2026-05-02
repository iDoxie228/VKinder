from infrastructure.config.settings import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DSN = DATABASE_URL
engine = create_engine(
        DSN,
        client_encoding = "utf-8"
    )
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()