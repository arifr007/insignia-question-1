import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    POSTGRES_URI = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET = os.getenv("JWT_SECRET", "fallback_jwt_secret")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # CORS origins configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:4173,http://127.0.0.1:3000,http://127.0.0.1:4173,https://insignia-question-1.pages.dev").split(",")