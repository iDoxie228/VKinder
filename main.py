from infrastructure.db.init_db import init_database
from app.bot import run_bot


def main():
    init_database()
    run_bot()


if __name__ == "__main__":
    main()