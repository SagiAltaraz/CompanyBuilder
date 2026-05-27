from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    postgres_url: str = "postgresql://founderai:founderai_secret@postgres:5432/founderai"
    redis_url: str = "redis://redis:6379"
    kafka_bootstrap_servers: str = "kafka:9092"
    chroma_host: str = "chromadb"
    chroma_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
