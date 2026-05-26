"""Benchmark the running chat API for latency and simple accuracy.

Input formats:
- JSON: a list of cases, or {"cases": [...]}
- JSONL: one case object per line
- TXT: one question per line, latency only

Case fields:
- id: optional case id
- question: required
- role: optional, one of employee/hr/manager/admin
- api_key: optional, overrides role
- expected_intent: optional
- expected_any: optional list of strings, at least one must appear in answer
- expected_all: optional list of strings, all must appear in answer
- expected_answer_contains: optional string or list; alias for expected_all
- category: optional; IN_SCOPE/HR map to document_qa, OUT_OF_SCOPE maps to out_of_scope
- answer: optional reference answer; scored by normalized token overlap
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx


DEFAULT_ENDPOINT = "http://127.0.0.1:8000/api/chat"
ROLE_KEYS = {
    "employee": "demo_employee_001",
    "hr": "demo_hr_001",
    "manager": "demo_manager_001",
    "admin": "demo_admin_001",
}
CATEGORY_INTENTS = {
    "IN_SCOPE": "document_qa",
    "HR": "document_qa",
    "OUT_OF_SCOPE": "out_of_scope",
}
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is",
    "it", "of", "on", "or", "that", "the", "this", "to", "with",
    "ai", "bi", "cac", "can", "cho", "co", "cua", "duoc", "gi", "hoac", "khi",
    "khong", "la", "lam", "mot", "nao", "nay", "nguoi", "nhan", "nhung", "qua",
    "sau", "se", "thi", "trong", "tu", "va", "ve", "voi",
}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    return " ".join(value.casefold().split())


def repair_mojibake(value: str) -> str:
    if "Ã" not in value and "Ä" not in value and "Æ" not in value:
        return value
    try:
        repaired = value.encode("cp1252").decode("utf-8")
    except UnicodeError:
        return value
    return repaired if repaired.count("�") <= value.count("�") else value


def repair_case_text(case: dict[str, Any]) -> None:
    for key in ("question", "answer"):
        if isinstance(case.get(key), str):
            case[key] = repair_mojibake(case[key])


def content_tokens(value: str) -> set[str]:
    tokens = set()
    for token in normalize_text(value).split():
        if len(token) >= 3 and token not in STOPWORDS:
            tokens.add(token)
    return tokens


def answer_overlap(reference: str, answer: str) -> float:
    reference_tokens = content_tokens(reference)
    if not reference_tokens:
        return 0.0
    answer_tokens = content_tokens(answer)
    return len(reference_tokens & answer_tokens) / len(reference_tokens)


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def load_cases(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8-sig").strip()
    if not raw:
        raise ValueError(f"{path} is empty")

    if path.suffix.lower() == ".jsonl":
        cases = [json.loads(line) for line in raw.splitlines() if line.strip()]
    elif path.suffix.lower() == ".txt":
        cases = [
            {"id": f"q-{idx:03d}", "question": line.strip()}
            for idx, line in enumerate(raw.splitlines(), start=1)
            if line.strip()
        ]
    else:
        data = json.loads(raw)
        cases = data.get("cases", data) if isinstance(data, dict) else data

    if not isinstance(cases, list):
        raise ValueError("Input must be a list of cases or an object with a cases list")

    normalized_cases: list[dict[str, Any]] = []
    for idx, case in enumerate(cases, start=1):
        if isinstance(case, str):
            case = {"question": case}
        if not isinstance(case, dict):
            raise ValueError(f"Case #{idx} is not an object")
        repair_case_text(case)
        question = str(case.get("question", "")).strip()
        if not question:
            raise ValueError(f"Case #{idx} is missing question")
        case.setdefault("id", f"q-{idx:03d}")
        normalized_cases.append(case)
    return normalized_cases


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    index = round((len(ordered) - 1) * pct)
    return ordered[index]


def score_case(case: dict[str, Any], response: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    answer = normalize_text(response.get("answer"))
    intent = response.get("intent")

    checks = 0
    passed = 0

    expected_intent = case.get("expected_intent")
    if not expected_intent and case.get("category"):
        expected_intent = CATEGORY_INTENTS.get(str(case["category"]).upper())
    if expected_intent:
        checks += 1
        if intent == expected_intent:
            passed += 1
        else:
            reasons.append(f"intent expected {expected_intent}, got {intent}")

    expected_all = as_list(case.get("expected_all"))
    expected_all.extend(as_list(case.get("expected_answer_contains")))
    if expected_all:
        checks += 1
        missing = [item for item in expected_all if normalize_text(item) not in answer]
        if not missing:
            passed += 1
        else:
            reasons.append("missing all-check terms: " + "; ".join(missing))

    expected_any = as_list(case.get("expected_any"))
    if expected_any:
        checks += 1
        if any(normalize_text(item) in answer for item in expected_any):
            passed += 1
        else:
            reasons.append("missing any-check terms: " + "; ".join(expected_any))

    reference_answer = case.get("answer")
    if reference_answer and not expected_all and not expected_any:
        checks += 1
        overlap = answer_overlap(str(reference_answer), str(response.get("answer") or ""))
        threshold = float(case.get("answer_min_overlap", 0.35))
        if overlap >= threshold:
            passed += 1
        else:
            reasons.append(f"answer overlap {overlap:.2f} below {threshold:.2f}")

    if response.get("error"):
        reasons.append(f"api error: {response['error']}")

    if checks == 0:
        return "Not scored", reasons
    if passed == checks and not response.get("error"):
        return "Pass", reasons
    if passed > 0:
        return "Partial", reasons
    return "Fail", reasons


def run_case(
    client: httpx.Client,
    endpoint: str,
    case: dict[str, Any],
    default_api_key: str,
    session_prefix: str,
    index: int,
) -> dict[str, Any]:
    role = str(case.get("role", "")).strip().lower()
    api_key = case.get("api_key") or ROLE_KEYS.get(role) or default_api_key
    payload = {
        "message": case["question"],
        "session_id": case.get("session_id") or f"{session_prefix}-{index:03d}",
    }

    started = time.perf_counter()
    try:
        http_response = client.post(
            endpoint,
            headers={"X-API-Key": api_key},
            json=payload,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        try:
            response_json = http_response.json()
        except Exception:
            response_json = {"answer": http_response.text, "intent": None}
        if http_response.status_code >= 400:
            response_json.setdefault(
                "error",
                {"code": f"HTTP_{http_response.status_code}", "message": http_response.text},
            )
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        response_json = {
            "answer": None,
            "intent": None,
            "sources": [],
            "error": {"code": "CLIENT_ERROR", "message": str(exc)},
        }

    result, reasons = score_case(case, response_json)
    expected_intent = case.get("expected_intent")
    if not expected_intent and case.get("category"):
        expected_intent = CATEGORY_INTENTS.get(str(case["category"]).upper())
    return {
        "id": case["id"],
        "question": case["question"],
        "expected_intent": expected_intent,
        "actual_intent": response_json.get("intent"),
        "latency_ms": latency_ms,
        "result": result,
        "reasons": reasons,
        "answer": response_json.get("answer"),
        "sources": response_json.get("sources", []),
        "error": response_json.get("error"),
        "raw_response": response_json,
    }


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [item["latency_ms"] for item in results]
    scored = [item for item in results if item["result"] != "Not scored"]
    passed = [item for item in scored if item["result"] == "Pass"]
    errors = [item for item in results if item.get("error")]

    by_intent: dict[str, dict[str, int]] = {}
    for item in scored:
        intent = item.get("expected_intent") or "unspecified"
        bucket = by_intent.setdefault(intent, {"total": 0, "pass": 0})
        bucket["total"] += 1
        if item["result"] == "Pass":
            bucket["pass"] += 1

    return {
        "total_questions": len(results),
        "scored_questions": len(scored),
        "request_errors": len(errors),
        "accuracy": (len(passed) / len(scored)) if scored else None,
        "pass_count": len(passed),
        "avg_latency_ms": int(statistics.mean(latencies)) if latencies else 0,
        "p95_latency_ms": percentile(latencies, 0.95),
        "min_latency_ms": min(latencies) if latencies else 0,
        "max_latency_ms": max(latencies) if latencies else 0,
        "by_intent": by_intent,
    }


def write_reports(output_dir: Path, summary: dict[str, Any], results: list[dict[str, Any]]) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"benchmark_results_{stamp}.json"
    md_path = output_dir / f"benchmark_report_{stamp}.md"

    json_path.write_text(
        json.dumps({"summary": summary, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    accuracy = "N/A" if summary["accuracy"] is None else f"{summary['accuracy'] * 100:.1f}%"
    lines = [
        "# Chat Benchmark Report",
        "",
        f"- Run time: {datetime.now().isoformat(timespec='seconds')}",
        f"- Total questions: {summary['total_questions']}",
        f"- Scored questions: {summary['scored_questions']}",
        f"- Request errors: {summary['request_errors']}",
        f"- Accuracy: {accuracy} ({summary['pass_count']} / {summary['scored_questions']})",
        f"- Average latency: {summary['avg_latency_ms']} ms",
        f"- P95 latency: {summary['p95_latency_ms']} ms",
        f"- Min latency: {summary['min_latency_ms']} ms",
        f"- Max latency: {summary['max_latency_ms']} ms",
        "",
        "## Case Results",
        "",
        "| ID | Intent | Latency | Result | Notes |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for item in results:
        notes = "; ".join(item["reasons"]) if item["reasons"] else ""
        intent = item.get("actual_intent") or ""
        lines.append(f"| {item['id']} | {intent} | {item['latency_ms']} ms | {item['result']} | {notes} |")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark a running HR RAG chat API.")
    parser.add_argument("input", type=Path, help="Path to JSON, JSONL, or TXT question file")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key", default="demo_hr_001")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--output-dir", type=Path, default=Path("docs"))
    args = parser.parse_args()

    cases = load_cases(args.input)
    session_prefix = "benchmark-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    results: list[dict[str, Any]] = []

    with httpx.Client(timeout=args.timeout) as client:
        for index, case in enumerate(cases, start=1):
            result = run_case(client, args.endpoint, case, args.api_key, session_prefix, index)
            results.append(result)
            print(
                f"{result['id']}: {result['result']} "
                f"{result['latency_ms']}ms intent={result.get('actual_intent')}"
            )

    summary = build_summary(results)
    json_path, md_path = write_reports(args.output_dir, summary, results)

    accuracy = "N/A" if summary["accuracy"] is None else f"{summary['accuracy'] * 100:.1f}%"
    print()
    print(f"Total: {summary['total_questions']}")
    print(f"Accuracy: {accuracy} ({summary['pass_count']} / {summary['scored_questions']})")
    print(f"Average latency: {summary['avg_latency_ms']} ms")
    print(f"P95 latency: {summary['p95_latency_ms']} ms")
    print(f"JSON: {json_path}")
    print(f"Report: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
