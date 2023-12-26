from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    json_projects_id_name: str = f"{BASE_DIR}/projects_id_name.json"
    db_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/db/records.db"
    db_url1: str = f"sqlite:///{BASE_DIR}/db/records.db"
    # logger_info: str = f"{BASE_DIR}/logger/app_info.log"
    # logger_error: str = f"{BASE_DIR}/logger/app_error.log"
    db_echo: bool = False
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"


settings = Settings()
