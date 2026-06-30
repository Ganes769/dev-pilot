data=lambda: [
    {
        "input": {
            "question": case["question"],
            "limit": 10,
        },
        "expected": {
            "expected_files": case["expected_files"],
            "expected_keywords": case["expected_keywords"],
            "min_sources": case.get("min_sources", 1),
        },
        "metadata": {"name": case["name"]},
    }
    for case in cases  # pyright: ignore[reportUndefinedVariable]
]