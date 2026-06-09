from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": str(Path(__file__).parent.parent / ".env")}

    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "todo_app"

    UPLOAD_DIR: str = "uploads"

    JWT_SECRET_KEY: str = "change-me-in-production-use-a-random-string"


settings = Settings()
