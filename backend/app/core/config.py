from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./hotel.db"
    secret_key: str = "development-only-change-me"
    frontend_url: str = "http://localhost:3000"
    payment_provider: str = "mock"
    hold_minutes: int = 15

settings = Settings()
