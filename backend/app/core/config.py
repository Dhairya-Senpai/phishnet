from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "Phishnet"
    debug: bool = False
    secret_key: str = "change-me"
    api_key: str = "change-me"

    # Database
    database_url: str = "postgresql://phishnet:phishnet@localhost:5432/phishnet"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]

    # Mail
    postfix_pipe_dir: str = "/var/mail/phishnet"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
