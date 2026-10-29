def evaluate_response(response: dict, test_case: dict) -> dict:
    """Evaluate a NexaDesk response against a test case."""

    checks = {}

    required_fields = {
        "id",
        "answer",
        "category",
        "escalate",
        "session_id",
        "usage",
        "meta",
    }

    checks["response_structure"] = required_fields.issubset(
        response.keys()
    )

    answer = response.get("answer", "")
    checks["answer_not_empty"] = (
        isinstance(answer, str) and bool(answer.strip())
    )

    checks["expected_category"] = (
        response.get("category") == test_case["expected_category"]
    )

    checks["expected_answer_keywords"] = all(
        keyword.lower() in answer.lower()
        for keyword in test_case["expected_answer_keywords"]
    )

    checks["escalate_is_boolean"] = isinstance(
        response.get("escalate"), bool
    )

    checks["session_id_present"] = bool(
        response.get("session_id", "").strip()
    ) if isinstance(response.get("session_id"), str) else False

    usage = response.get("usage", {})
    checks["usage_metrics_present"] = (
        isinstance(usage, dict)
        and all(
            isinstance(usage.get(field), int)
            for field in (
                "input_tokens",
                "output_tokens",
                "latency_ms",
            )
        )
    )

    meta = response.get("meta", {})
    checks["model_metadata_present"] = (
        isinstance(meta, dict)
        and isinstance(meta.get("model"), str)
        and isinstance(meta.get("prompt_version"), str)
    )

    return {
        "test_case_id": test_case["id"],
        "test_case_name": test_case["name"],
        "checks": checks,
        "passed": all(checks.values()),
    }