from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app import PROJECT_DIR


class Settings(BaseSettings):
    DATABASE_FILE_PATH: Path = "app.db"
    DATABASE_ECHO: bool = False
    AUTO_COMPLETE_PROJECTS: bool = True
    AUTO_ADJUST_TASK_DEADLINES: bool = True

    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        if self.DATABASE_FILE_PATH.is_dir():
            self.DATABASE_FILE_PATH.mkdir(exist_ok=True)
        return f"sqlite:///{str(self.DATABASE_FILE_PATH)}"


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
