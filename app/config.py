import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "luminary_notes"

    # Embedding
    embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"
    hf_token: str = ""
    # transformer_offline: int = 1
    vector_size: int = 1024

    # Retrieval
    top_k: int = 5
    score_threshold: float = 0.45

    # Groq
    api_key: str = ""
    generative_model: str = "llama-3.3-70b-versatile"
    max_tokens: int = 1024
    temperature: float = 0.2

    # App
    app_name: str = "Luminary"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

os.environ["TRANSFORMERS_OFFLINE"] = "1"

if settings.hf_token:
    os.environ["HF_TOKEN"] = settings.hf_token
