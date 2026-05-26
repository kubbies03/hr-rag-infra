"""Call the chat API for markdown test cases and save answers to a markdown file.

Input:
- Markdown table with question rows, such as docs/rag_chatbot_30_testcases-converted.md

Output:
- Markdown report with each question, intent, answer, and source list
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any
import sys

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benchmark_chat import repair_mojibake, run_case


def parse_markdown_cases(path: Path) -> list[dict[str, Any]]:
    """Extract test cases from a markdown table."""
    raw = path.read_text(encoding="utf-8-sig").splitlines()
    cases: list[dict[str, Any]] = []

    for line in raw:
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if stripped.startswith("| ---"):
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue

        case_id = cells[0]
        if not case_id.isdigit():
            continue

        group = cells[1]
        question = repair_mojibake(cells[2])
        expected_answer = repair_mojibake(cells[3])
        source_file = repair_mojibake(cells[4]) if len(cells) > 4 else ""
        grounding = repair_mojibake(cells[6]) if len(cells) > 6 else ""

        cases.append(
            {
                "id": case_id,
                "group": group,
                "question": question,
                "expected_answer": expected_answer,
                "source_file": source_file,
                "grounding": grounding,
                "session_id": f"md-{case_id.zfill(3)}",
            }
        )

    return cases


def _render_sources(sources: list[dict[str, Any]]) -> list[str]:
    if not sources:
        return ["- Không có nguồn trả về"]

    lines: list[str] = []
    for source in sources:
        parts = []
        if source.get("title"):
            parts.append(f"title={source['title']}")
        if source.get("file"):
            parts.append(f"file={source['file']}")
        if source.get("page") is not None:
            parts.append(f"page={source['page']}")
        if source.get("category"):
            parts.append(f"category={source['category']}")
        lines.append(f"- {', '.join(parts) if parts else str(source)}")
    return lines


def write_markdown_report(
    output_file: Path,
    source_file: Path,
    results: list[dict[str, Any]],
) -> Path:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")

    lines: list[str] = [
        "# Chat Answers",
        "",
        f"- Source: `{source_file.name}`",
        f"- Generated at: {stamp}",
        f"- Total cases: {len(results)}",
        "",
    ]

    for item in results:
        sources = item.get("sources", [])
        lines.extend(
            [
                f"## {item['id']}. {item['group']}",
                "",
                f"**Câu hỏi:** {item['question']}",
                "",
                f"**Intent:** `{item.get('actual_intent') or ''}`",
                "",
                "**Câu trả lời:**",
                "",
                item.get("answer") or "_Không có câu trả lời_",
                "",
                "**Nguồn:**",
                "",
                *_render_sources(sources),
                "",
            ]
        )

    output_file.write_text("\n".join(lines), encoding="utf-8")
    return output_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Call the chat API for markdown test cases and save answers to a markdown file."
    )
    parser.add_argument("input", type=Path, help="Path to the markdown testcase file")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/api/chat")
    parser.add_argument("--api-key", default="demo_hr_001")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help="Output markdown file path. Defaults to docs/<input_stem>_answers.md",
    )
    args = parser.parse_args()

    cases = parse_markdown_cases(args.input)
    if not cases:
        raise ValueError(f"No markdown testcase rows found in {args.input}")

    output_file = args.output_file or args.input.with_name(f"{args.input.stem}_answers.md")
    session_prefix = "md-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    results: list[dict[str, Any]] = []

    with httpx.Client(timeout=args.timeout) as client:
        for index, case in enumerate(cases, start=1):
            result = run_case(
                client=client,
                endpoint=args.endpoint,
                case=case,
                default_api_key=args.api_key,
                session_prefix=session_prefix,
                index=index,
            )
            result["group"] = case["group"]
            result["expected_answer"] = case["expected_answer"]
            result["source_file"] = case["source_file"]
            result["grounding"] = case["grounding"]
            results.append(result)
            print(
                f"{result['id']}: {result['result']} "
                f"{result['latency_ms']}ms intent={result.get('actual_intent')}"
            )

    saved_path = write_markdown_report(output_file, args.input, results)
    print()
    print(f"Saved markdown: {saved_path}")
    print(f"Total cases: {len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
