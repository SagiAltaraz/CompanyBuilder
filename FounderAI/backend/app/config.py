from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    postgres_url: str = "postgresql://founderai:founderai_secret@postgres:5432/founderai"
    redis_url: str = "redis://redis:6379"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
