from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = "change_me_locally"

    database_url: str = "postgresql+psycopg://signallens:signallens@localhost:5432/signallens"

    llm_provider: Literal["mock", "gemini", "groq"] = "mock"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    gemini_fallback_model: str = "gemini-2.5-flash"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    sentiment_model: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    demo_user_email: str = "demo@signallens.app"
    demo_user_password: str = "SignalLens_Demo2026!"

    backend_cors_origins: list[str] = ["http://localhost:3000"]

    duplicate_similarity_threshold: float = 0.92
    rolling_baseline_days: int = 28
    short_baseline_days: int = 7
    emerging_issue_similarity_threshold: float = 0.45


@lru_cache
def get_settings() -> Settings:
    return Settings()
