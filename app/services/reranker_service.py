"""Optional Gemini-based reranking for retrieved chunks."""

import json
import logging
import re

from langchain_core.messages import HumanMessage

from app.core.config import settings
from app.services.gemini_service import _invoke_with_timeout, get_llm

logger = logging.getLogger(__name__)

_RERANK_PROMPT = """You are a document reranker for a retrieval system.
Given one user question and a list of candidate passages, score each passage from 0.0 to 1.0.

Rules:
- Score higher when the passage directly helps answer the question.
- Score lower when the passage is off-topic, too generic, or only weakly related.
- Return valid JSON only.
- Output format:
{"scores":[{"index":0,"score":0.91},{"index":1,"score":0.12}]}

Question:
{query}

Candidate passages:
{documents}
"""


def _provider() -> str:
    return settings.RERANKER_PROVIDER.strip().lower()


def _clip_text(text: str) -> str:
    limit = settings.RERANKER_MAX_DOC_CHARS
    return text if len(text) <= limit else text[:limit] + "..."


def _build_documents_block(documents: list[dict]) -> str:
    blocks = []
    for i, doc in enumerate(documents):
        meta = doc.get("metadata", {})
        title = meta.get("title", "Unknown")
        section = meta.get("section_title", "")
        header = f"[{i}] title={title}"
        if section:
            header += f" section={section}"
        blocks.append(f"{header}\n{_clip_text(doc['content'])}")
    return "\n\n".join(blocks)


def _parse_scores(raw: str) -> dict[int, float]:
    raw = raw.strip()
    raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw).strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}

    scores: dict[int, float] = {}
    for item in data.get("scores", []):
        try:
            idx = int(item["index"])
            score = float(item["score"])
        except (KeyError, TypeError, ValueError):
            continue
        scores[idx] = max(0.0, min(1.0, score))
    return scores


def _rerank_with_gemini(query: str, documents: list[dict]) -> list[dict]:
    llm = get_llm()
    prompt = _RERANK_PROMPT.format(
        query=query,
        documents=_build_documents_block(documents),
    )
    response = _invoke_with_timeout(
        llm,
        [HumanMessage(content=prompt)],
        timeout=settings.RERANKER_TIMEOUT,
    )
    scores = _parse_scores(response.content if hasattr(response, "content") else str(response))
    if not scores:
        logger.warning("Gemini reranker returned unparsable scores; falling back to vector order.")
        return documents

    rescored = []
    for i, doc in enumerate(documents):
        doc["reranker_score"] = scores.get(i, 0.0)
        rescored.append(doc)
    return sorted(rescored, key=lambda d: d["reranker_score"], reverse=True)


def rerank(query: str, documents: list[dict], top_k: int = None) -> list[dict]:
    """Rerank candidate documents by relevance."""
    if not documents:
        return []

    if top_k is None:
        top_k = settings.RETRIEVER_TOP_K

    provider = _provider()
    if provider == "gemini":
        try:
            ranked = _rerank_with_gemini(query, documents)
        except Exception as e:
            logger.warning("Gemini reranker failed: %s. Falling back to vector order.", e)
            ranked = documents
    else:
        logger.info("Reranker provider '%s' is disabled or unsupported. Using vector order.", provider)
        ranked = documents

    logger.debug(
        "Reranker scores (top %d of %d candidates): %s",
        min(top_k, len(ranked)),
        len(ranked),
        [
            (round(d.get("reranker_score", 0.0), 3), d["metadata"].get("section_title", "")[:40])
            for d in ranked[:top_k]
        ],
    )

    filtered = [d for d in ranked if d.get("reranker_score", 1.0) >= settings.RERANKER_MIN_SCORE]

    if not filtered:
        logger.info(
            "Reranker: all %d candidates below threshold %.2f, falling back to vector top-%d.",
            len(ranked),
            settings.RERANKER_MIN_SCORE,
            top_k,
        )
        return ranked[:top_k]

    return filtered[:top_k]
