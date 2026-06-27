import argparse
import json
from pathlib import Path

import requests


BAD_ANSWER_MARKERS = [
    "I could not find enough evidence",
    "could not find evidence",
    "No answer",
]


def ask_api(base_url: str, question: str, limit: int):
    response = requests.post(
        f"{base_url}/ask",
        json={"question": question, "limit": limit},
        timeout=180,
    )
    response.raise_for_status()
    return response.json()


def contains_expected_file(sources, expected_file: str) -> bool:
    return any(source.get("file_path") == expected_file for source in sources)


def keyword_hits(answer: str, keywords: list[str]) -> list[str]:
    lowered = answer.lower()
    return [keyword for keyword in keywords if keyword.lower() in lowered]


def run_case(base_url: str, case: dict, limit: int) -> dict:
    data = ask_api(base_url, case["question"], limit)

    answer = data.get("answer", "")
    sources = data.get("sources", [])

    bad_answer = any(marker.lower() in answer.lower() for marker in BAD_ANSWER_MARKERS)

    expected_files = case.get("expected_files", [])
    found_files = [
        expected_file
        for expected_file in expected_files
        if contains_expected_file(sources, expected_file)
    ]

    expected_keywords = case.get("expected_keywords", [])
    found_keywords = keyword_hits(answer, expected_keywords)

    min_sources = case.get("min_sources", 1)

    passed = (
        not bad_answer
        and len(sources) >= min_sources
        and len(found_files) == len(expected_files)
        and len(found_keywords) == len(expected_keywords)
    )

    return {
        "name": case["name"],
        "question": case["question"],
        "passed": passed,
        "bad_answer": bad_answer,
        "source_count": len(sources),
        "expected_files": expected_files,
        "found_files": found_files,
        "expected_keywords": expected_keywords,
        "found_keywords": found_keywords,
        "answer": answer,
        "sources": sources,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="evals/cases.json")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default="evals/results.json")
    args = parser.parse_args()

    cases = json.loads(Path(args.cases).read_text())

    results = []
    for case in cases:
        result = run_case(args.base_url, case, args.limit)
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status}: {result['name']}")
        if not result["passed"]:
            print(f"  Question: {result['question']}")
            print(f"  Found files: {result['found_files']}")
            print(f"  Found keywords: {result['found_keywords']}")
            print(f"  Sources: {[s.get('file_path') for s in result['sources']]}")

    passed = sum(1 for result in results if result["passed"])
    total = len(results)

    report = {
        "passed": passed,
        "total": total,
        "pass_rate": round(passed / total, 3) if total else 0,
        "results": results,
    }

    Path(args.output).write_text(json.dumps(report, indent=2))
    print(f"\nPassed {passed}/{total}")
    print(f"Saved report to {args.output}")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()