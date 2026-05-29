from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MISTRAL_API_KEY: str
    MONGO_URI: str
    GMAIL_SENDER: str
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    GMAIL_REFRESH_TOKEN: str
    OUTPUT_FOLDER: str = "outputs"

    # Local:  http://127.0.0.1:8000
    # Server: https://yourdomain.com
    API_BASE_URL: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"

settings = Settings()
