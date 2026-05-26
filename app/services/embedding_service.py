"""Gemini embedding wrapper for retrieval and ingest."""

import threading

from langchain_google_genai import GoogleGenerativeAIEmbeddings

_embed_cache = threading.local()
_model_lock = threading.Lock()

from app.core.config import settings

_model: GoogleGenerativeAIEmbeddings | None = None


def _get_model() -> GoogleGenerativeAIEmbeddings:
    """Return the singleton Gemini embeddings client."""
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                _model = GoogleGenerativeAIEmbeddings(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    google_api_key=settings.GOOGLE_API_KEY,
                    request_options={"timeout": settings.GEMINI_EMBEDDING_TIMEOUT},
                )
    return _model


def get_embeddings():
    """Return the embeddings client used by ingest and retriever services."""
    return _EmbeddingsAdapter(_get_model())


class _EmbeddingsAdapter:
    """Expose the embed_query and embed_documents interface expected by callers."""

    def __init__(self, model: GoogleGenerativeAIEmbeddings):
        self._model = model

    def embed_query(self, text: str) -> list[float]:
        cached = getattr(_embed_cache, "last", None)
        if cached is not None and cached[0] == text:
            return cached[1]
        result = self._model.embed_query(
            text,
            task_type="retrieval_query",
        )
        _embed_cache.last = (text, result)
        return result

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._model.embed_documents(
            texts,
            batch_size=settings.GEMINI_EMBEDDING_BATCH_SIZE,
            task_type="retrieval_document",
        )


def embed_query(text: str) -> list[float]:
    return get_embeddings().embed_query(text)


def embed_documents(texts: list[str]) -> list[list[float]]:
    return get_embeddings().embed_documents(texts)
