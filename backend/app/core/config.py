from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://teleuser:telepass@db:5432/teleconnect")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    APP_NAME: str = "TeleConnect API"

settings = Settings()