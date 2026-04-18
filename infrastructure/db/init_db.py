from session import Base, engine
from infrastructure.db import models

def init_database():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_database()