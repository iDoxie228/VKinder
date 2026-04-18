import os 
from dotenv import load_dotenv

load_dotenv()

DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")

VK_GROUP_TOKEN=os.getenv("VK_GROUP_TOKEN")
VK_USER_TOKEN=os.getenv("VK_USER_TOKEN")
VK_API_VERSION=os.getenv("VK_API_VERSION")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"