from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "CHANGE_ME_TO_RANDOM_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24  # 1 day
    UPLOAD_DIR: str = "./uploads"

settings = Settings()