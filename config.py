import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", "samantabasu2001")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Mongodb@basu1234")
    MONGO_CLUSTER = os.getenv("MONGO_CLUSTER", "quester06.4lhez.mongodb.net")
    MONGO_DB = os.getenv("MONGO_DB", "flask_app")
    MONGO_URI = (
        f"mongodb+srv://{quote_plus(MONGO_USERNAME)}:{quote_plus(MONGO_PASSWORD)}@{MONGO_CLUSTER}/"
        f"{MONGO_DB}?retryWrites=true&w=majority"
    )