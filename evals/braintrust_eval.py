"""
Braintrust eval runner for DevPilot.

Usage:
    # Install deps first
    pip install braintrust autoevals

    # Set your API key in .env
    BRAINTRUST_API_KEY=sk-...

    # Make sure the API server is running and this repo is indexed, then:
    braintrust eval evals/braintrust_eval.py

    # Or directly:
    python evals/braintrust_eval.py
"""

import json
import os
from pathlib import Path

import requests
from autoevals import Score
from braintrust import Eval
from dotenv import load_dotenv

# Load .env before Braintrust tries to read BRAINTRUST_API_KEY
load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL = os.getenv("DEVPILOT_URL", "http://127.0.0.1:8000")
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.4"))
CASES_PATH = Path(__file__).parent / "cases.json"

BAD_ANSWER_MARKERS = [
    "i could not find enough evidence",
    "could not find evidence",
    "no answer",
]

# ---------------------------------------------------------------------------
# Dataset — loaded from evals/cases.json
# ---------------------------------------------------------------------------

_cases = json.loads(CASES_PATH.read_text())


def build_dataset():
    return [
        {
            "input": {
                "question": case["question"],
                "limit": 10,
                "score_threshold": SCORE_THRESHOLD,
            },
            "expected": {
                "expected_files": case.get("expected_files", []),
                "expected_keywords": case.get("expected_keywords", []),
                "min_sources": case.get("min_sources", 1),
            },
            "metadata": {"name": case["name"]},
        }
        for case in _cases
    ]


# ---------------------------------------------------------------------------
# Task — calls POST /ask on the running DevPilot API
# ---------------------------------------------------------------------------


def task(input):
    resp = requests.post(
        f"{BASE_URL}/ask",
        json=input,
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()  # {"question": ..., "answer": ..., "sources": [...]}


# ---------------------------------------------------------------------------
# Scorers
# ---------------------------------------------------------------------------


def files_found(output, expected, **kwargs):
    """Score 0–1: fraction of expected source files found in the response."""
    sources = output.get("sources", [])
    source_paths = {s.get("file_path", "") for s in sources}
    expected_files = expected.get("expected_files", [])

    if not expected_files:
        return Score(name="files_found", score=1.0, metadata={"reason": "no expected files"})

    found = [f for f in expected_files if f in source_paths]
    score = len(found) / len(expected_files)

    return Score(
        name="files_found",
        score=score,
        metadata={
            "found": found,
            "missing": [f for f in expected_files if f not in source_paths],
            "expected": expected_files,
            "all_sources": list(source_paths),
        },
    )


def keywords_found(output, expected, **kwargs):
    """Score 0–1: fraction of expected keywords present in the answer."""
    answer = output.get("answer", "").lower()
    expected_keywords = expected.get("expected_keywords", [])

    if not expected_keywords:
        return Score(name="keywords_found", score=1.0, metadata={"reason": "no expected keywords"})

    found = [k for k in expected_keywords if k.lower() in answer]
    score = len(found) / len(expected_keywords)

    return Score(
        name="keywords_found",
        score=score,
        metadata={
            "found": found,
            "missing": [k for k in expected_keywords if k.lower() not in answer],
            "expected": expected_keywords,
        },
    )


def no_bad_answer(output, **kwargs):
    """Score 1.0 if answer is substantive, 0.0 if it's a refusal/no-evidence response."""
    answer = output.get("answer", "").lower()
    is_bad = any(marker in answer for marker in BAD_ANSWER_MARKERS)

    return Score(
        name="no_bad_answer",
        score=0.0 if is_bad else 1.0,
        metadata={"answer_preview": output.get("answer", "")[:200]},
    )


def min_sources_met(output, expected, **kwargs):
    """Score 1.0 if the response returned at least min_sources sources."""
    sources = output.get("sources", [])
    min_required = expected.get("min_sources", 1)
    met = len(sources) >= min_required

    return Score(
        name="min_sources_met",
        score=1.0 if met else 0.0,
        metadata={"sources_returned": len(sources), "min_required": min_required},
    )


# ---------------------------------------------------------------------------
# Eval entry point
# ---------------------------------------------------------------------------

Eval(
    "devpilot",
    data=build_dataset,
    task=task,
    scores=[files_found, keywords_found, no_bad_answer, min_sources_met],
    metadata={
        "base_url": BASE_URL,
        "score_threshold": SCORE_THRESHOLD,
        "cases_file": str(CASES_PATH),
    },
)
