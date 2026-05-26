"""Compare expected answers from a testcase markdown file with actual answers.

Produces a markdown report with:
- overall accuracy-style summary
- breakdown by policy group
- per-case comparison table
"""

from __future__ import annotations

import argparse
import re
import statistics
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is",
    "it", "of", "on", "or", "that", "the", "this", "to", "with",
    "ai", "bi", "cac", "can", "cho", "co", "cua", "duoc", "gi", "hoac", "khi",
    "khong", "la", "lam", "mot", "nao", "nay", "nguoi", "nhan", "nhung", "qua",
    "sau", "se", "thi", "trong", "tu", "va", "ve", "voi",
}

FALLBACK_PHRASES = (
    "khong tim thay thong tin phu hop",
    "khong xac dinh duoc",
    "khong co thong tin",
)


@dataclass
class CaseRow:
    id: int
    group: str
    question: str
    expected: str
    actual: str
    intent: str
    sources: int


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = value.casefold()
    value = re.sub(r"[^\w\s]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def content_tokens(value: str) -> set[str]:
    tokens = set()
    for token in normalize_text(value).split():
        if len(token) >= 3 and token not in STOPWORDS:
            tokens.add(token)
    return tokens


def overlap_score(expected: str, actual: str) -> float:
    expected_tokens = content_tokens(expected)
    if not expected_tokens:
        return 0.0
    actual_tokens = content_tokens(actual)
    return len(expected_tokens & actual_tokens) / len(expected_tokens)


def classify_case(expected: str, actual: str) -> str:
    norm_actual = normalize_text(actual)
    if not norm_actual:
        return "Incorrect"
    if normalize_text(expected) == norm_actual:
        return "Exact"
    if any(phrase in norm_actual for phrase in FALLBACK_PHRASES):
        return "Incorrect"
    score = overlap_score(expected, actual)
    if score >= 0.75:
        return "Correct"
    if score >= 0.40:
        return "Partial"
    return "Incorrect"


def parse_source_cases(path: Path) -> dict[int, dict[str, str]]:
    raw = path.read_text(encoding="utf-8-sig")
    cases: dict[int, dict[str, str]] = {}
    for line in raw.splitlines():
        s = line.strip()
        if not s.startswith("|") or s.startswith("| ---"):
            continue
        cells = [cell.strip() for cell in s.strip("|").split("|")]
        if len(cells) < 4 or not cells[0].isdigit():
            continue
        cid = int(cells[0])
        cases[cid] = {
            "group": cells[1],
            "question": cells[2],
            "expected": cells[3],
        }
    return cases


def parse_output_cases(path: Path) -> dict[int, dict[str, Any]]:
    raw = path.read_text(encoding="utf-8-sig")
    parts = re.split(r"(?m)^##\s+(\d+)\.\s+.*$", raw)
    cases: dict[int, dict[str, Any]] = {}
    for i in range(1, len(parts), 2):
        cid = int(parts[i])
        body = parts[i + 1]

        question = ""
        intent = ""
        answer = ""
        sources = []

        q_match = re.search(r"\*\*Câu hỏi:\*\*\s*(.*?)\n\n\*\*Intent:", body, flags=re.S)
        if q_match:
            question = q_match.group(1).strip()

        intent_match = re.search(r"\*\*Intent:\*\*\s*`([^`]*)`", body)
        if intent_match:
            intent = intent_match.group(1).strip()

        ans_match = re.search(r"\*\*Câu trả lời:\*\*\s*\n\n(.*?)\n\n\*\*Nguồn:\*\*", body, flags=re.S)
        if ans_match:
            answer = ans_match.group(1).strip()

        source_lines = re.findall(r"(?m)^- (.+)$", body)
        sources = source_lines

        cases[cid] = {
            "question": question,
            "intent": intent,
            "answer": answer,
            "sources": sources,
        }
    return cases


def build_report(rows: list[CaseRow], source_file: Path, output_file: Path) -> str:
    total = len(rows)
    exact = sum(1 for row in rows if classify_case(row.expected, row.actual) == "Exact")
    correct = sum(1 for row in rows if classify_case(row.expected, row.actual) == "Correct")
    partial = sum(1 for row in rows if classify_case(row.expected, row.actual) == "Partial")
    incorrect = sum(1 for row in rows if classify_case(row.expected, row.actual) == "Incorrect")
    avg_overlap = statistics.mean(overlap_score(row.expected, row.actual) for row in rows) if rows else 0.0
    median_overlap = statistics.median(overlap_score(row.expected, row.actual) for row in rows) if rows else 0.0

    by_group: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_group.setdefault(row.group, {"total": 0, "exact": 0, "correct": 0, "partial": 0, "incorrect": 0})
        bucket["total"] += 1
        status = classify_case(row.expected, row.actual)
        bucket[status.lower()] += 1

    lines: list[str] = [
        "# Chat Answer Comparison Report",
        "",
        f"- Source file: `{source_file.name}`",
        f"- Output file: `{output_file.name}`",
        f"- Cases compared: {total}",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Exact match | {exact} |",
        f"| Correct | {correct} |",
        f"| Partial | {partial} |",
        f"| Incorrect | {incorrect} |",
        f"| Average overlap | {avg_overlap:.3f} |",
        f"| Median overlap | {median_overlap:.3f} |",
        "",
        "## Group Breakdown",
        "",
        "| Group | Total | Exact | Correct | Partial | Incorrect |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for group in sorted(by_group):
        bucket = by_group[group]
        lines.append(
            f"| {group} | {bucket['total']} | {bucket['exact']} | {bucket['correct']} | {bucket['partial']} | {bucket['incorrect']} |"
        )

    lines.extend([
        "",
        "## Per-Case Results",
        "",
        "| ID | Group | Status | Overlap | Intent | Sources |",
        "| --- | --- | --- | ---: | --- | ---: |",
    ])

    for row in rows:
        status = classify_case(row.expected, row.actual)
        score = overlap_score(row.expected, row.actual)
        lines.append(
            f"| {row.id} | {row.group} | {status} | {score:.3f} | {row.intent or ''} | {row.sources} |"
        )

    lines.extend([
        "",
        "## Notes",
        "",
        "- `Exact` means the normalized expected answer and actual answer are identical.",
        "- `Correct` means high lexical overlap with the expected answer after normalization.",
        "- `Partial` means moderate overlap and usually the same intent but different wording.",
        "- `Incorrect` includes fallback answers such as 'không tìm thấy thông tin' and weak overlaps.",
        "",
    ])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare expected and actual chat answers.")
    parser.add_argument("--source", type=Path, default=Path("docs/rag_chatbot_30_testcases-converted.md"))
    parser.add_argument("--output", type=Path, default=Path("docs/rag_chatbot_30_testcases-converted_answers.md"))
    parser.add_argument("--report", type=Path, default=Path("docs/rag_chatbot_30_testcases_comparison_report.md"))
    args = parser.parse_args()

    source_cases = parse_source_cases(args.source)
    output_cases = parse_output_cases(args.output)

    rows: list[CaseRow] = []
    for cid in sorted(source_cases):
        src = source_cases[cid]
        out = output_cases.get(cid, {})
        rows.append(
            CaseRow(
                id=cid,
                group=src["group"],
                question=src["question"],
                expected=src["expected"],
                actual=out.get("answer", ""),
                intent=out.get("intent", ""),
                sources=len(out.get("sources", [])),
            )
        )

    report = build_report(rows, args.source, args.output)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.report}")
    print(f"Compared {len(rows)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
