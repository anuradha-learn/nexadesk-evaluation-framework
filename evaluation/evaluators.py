def evaluate_response(response: dict, test_case: dict) -> dict:
    """Evaluate a NexaDesk response and explain each check result."""

    checks = {}
    details = {}

    def record_check(name: str, passed: bool, reason: str):
        checks[name] = passed
        details[name] = {
            "passed": passed,
            "reason": reason,
        }

    # Validate the top-level response structure.
    required_fields = {
        "answer",
        "category",
        "escalate",
        "session_id",
        "usage",
        "meta",
    }

    is_dict = isinstance(response, dict)

    if not is_dict:
        record_check(
            "response_structure",
            False,
            f"Expected a dictionary, received {type(response).__name__}.",
        )
        response = {}
    else:
        missing_fields = required_fields - response.keys()
        structure_passed = not missing_fields

        record_check(
            "response_structure",
            structure_passed,
            (
                "All required fields are present."
                if structure_passed
                else f"Missing required fields: {sorted(missing_fields)}."
            ),
        )

    # Validate the answer.
    answer = response.get("answer")
    answer_passed = isinstance(answer, str) and bool(answer.strip())

    record_check(
        "answer_not_empty",
        answer_passed,
        (
            "Answer is a non-empty string."
            if answer_passed
            else "Expected a non-empty string in the 'answer' field."
        ),
    )

    # Validate category.
    expected_category = test_case.get("expected_category")
    actual_category = response.get("category")

    category_passed = (
        actual_category == expected_category
        and bool(expected_category)
    )

    record_check(
        "expected_category",
        category_passed,
        (
            f"Category matched: {actual_category!r}."
            if category_passed
            else (
                f"Expected category {expected_category!r}, "
                f"received {actual_category!r}."
            )
        ),
    )

    # Validate expected keywords.
    keywords = test_case.get("expected_answer_keywords", [])

    keywords_passed = (
        isinstance(answer, str)
        and isinstance(keywords, list)
        and bool(keywords)
        and all(
            isinstance(keyword, str)
            and bool(keyword.strip())
            and keyword.lower() in answer.lower()
            for keyword in keywords
        )
    )

    if not isinstance(keywords, list) or not keywords:
        keyword_reason = "Expected keywords must be a non-empty list."
    elif not isinstance(answer, str):
        keyword_reason = "Cannot check keywords because the answer is not a string."
    else:
        matched = [
            keyword
            for keyword in keywords
            if isinstance(keyword, str)
            and bool(keyword.strip())
            and keyword.lower() in answer.lower()
        ]
        missing = [
            keyword
            for keyword in keywords
            if not isinstance(keyword, str)
            or not keyword.strip()
            or keyword.lower() not in answer.lower()
        ]

        keyword_reason = (
            f"All expected keywords found: {matched}."
            if keywords_passed
            else f"Missing or invalid expected keywords: {missing}."
        )

    record_check(
        "expected_answer_keywords",
        keywords_passed,
        keyword_reason,
    )

    # Validate escalation flag.
    escalate = response.get("escalate")
    escalate_passed = isinstance(escalate, bool)

    record_check(
        "escalate_is_boolean",
        escalate_passed,
        (
            f"Escalation flag is Boolean: {escalate!r}."
            if escalate_passed
            else (
                f"Expected a Boolean escalation flag, "
                f"received {type(escalate).__name__}."
            )
        ),
    )

    # Validate session ID.
    session_id = response.get("session_id")
    session_passed = (
        isinstance(session_id, str) and bool(session_id.strip())
    )

    record_check(
        "session_id_present",
        session_passed,
        (
            "Session ID is present."
            if session_passed
            else "Expected a non-empty string in the 'session_id' field."
        ),
    )

    # Validate usage metrics.
    usage = response.get("usage")
    usage_is_dict = isinstance(usage, dict)

    if not usage_is_dict:
        usage = {}

    required_metrics = {
        "input_tokens",
        "output_tokens",
        "latency_ms",
    }

    missing_metrics = required_metrics - usage.keys()

    invalid_metrics = [
        metric
        for metric in required_metrics
        if metric in usage
        and (
            type(usage[metric]) is not int
            or usage[metric] < 0
        )
    ]

    usage_passed = (
        usage_is_dict
        and not missing_metrics
        and not invalid_metrics
    )

    if usage_passed:
        usage_reason = "All required usage metrics are non-negative integers."
    elif not usage_is_dict:
        usage_reason = "Expected the 'usage' field to be a dictionary."
    else:
        problems = []
        if missing_metrics:
            problems.append(f"Missing metrics: {sorted(missing_metrics)}")
        if invalid_metrics:
            problems.append(f"Invalid metrics: {sorted(invalid_metrics)}")
        usage_reason = "; ".join(problems) + "."

    record_check(
        "usage_metrics_present",
        usage_passed,
        usage_reason,
    )

    # Validate model metadata.
    meta = response.get("meta")
    meta_is_dict = isinstance(meta, dict)

    if not meta_is_dict:
        meta = {}

    model = meta.get("model")
    prompt_version = meta.get("prompt_version")

    metadata_passed = (
        isinstance(model, str)
        and bool(model.strip())
        and isinstance(prompt_version, str)
        and bool(prompt_version.strip())
    )

    if metadata_passed:
        metadata_reason = (
            f"Model: {model}; prompt version: {prompt_version}."
        )
    else:
        metadata_reason = (
            "Expected non-empty strings for both 'meta.model' "
            "and 'meta.prompt_version'."
        )

    record_check(
        "model_metadata_present",
        metadata_passed,
        metadata_reason,
    )

    return {
        "test_case_id": test_case.get("id", "unknown"),
        "test_case_name": test_case.get("name", "unnamed"),
        "checks": checks,
        "details": details,
        "passed": all(checks.values()),
    }