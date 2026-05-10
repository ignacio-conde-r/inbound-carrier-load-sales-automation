from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/happyrobot.db"
    FMCSA_MODE: str = "mock"
    FMCSA_WEBKEY: str = ""
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
