"""Application configuration."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)


class Settings(BaseSettings):
    BASE_DIR: str = BASE_DIR
    GOOGLE_API_KEY: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.3

    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    GEMINI_EMBEDDING_BATCH_SIZE: int = 100
    GEMINI_EMBEDDING_TIMEOUT: int = 30
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_CREDENTIALS_PATH: str = os.path.join(BASE_DIR, "firebase-service-account.json")

    DATABASE_URL: str = "sqlite:///" + os.path.join(BASE_DIR, "data", "sqlite", "hr.db")

    CHROMA_PERSIST_DIR: str = os.path.join(BASE_DIR, "data", "chroma")
    CHROMA_COLLECTION_NAME: str = "hr_documents"
    ANONYMIZED_TELEMETRY: bool = False

    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 75
    RETRIEVER_TOP_K: int = 5          # Fix 9: was 2, too low for complex questions
    RETRIEVAL_CANDIDATE_K: int = 12   # Fix 9: was 5, expanded candidate pool
    MAX_CONVERSATION_HISTORY: int = 3  # Fix 4: was 1, now matches rag_service usage

    RERANKER_PROVIDER: str = "gemini"
    RERANKER_MIN_SCORE: float = 0.3
    RERANKER_TIMEOUT: int = 20
    RERANKER_MAX_DOC_CHARS: int = 1200
    USE_RERANKER: bool = False

    DOCS_DIR: str = os.path.join(BASE_DIR, "data", "docs")

    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
