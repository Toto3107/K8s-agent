from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_model: str = "anthropic/claude-3-haiku"
    kubeconfig_path: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
