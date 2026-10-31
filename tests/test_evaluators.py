import pytest

from evaluation.evaluators import evaluate_response


@pytest.fixture
def valid_response():
    return {
        "answer": (
            "You can reset your password through the company "
            "password portal."
        ),
        "category": "it_access",
        "escalate": False,
        "session_id": "test-session-001",
        "usage": {
            "input_tokens": 20,
            "output_tokens": 15,
            "latency_ms": 100,
        },
        "meta": {
            "model": "gpt-4o-mini",
            "prompt_version": "v1",
        },
    }


@pytest.fixture
def valid_test_case():
    return {
        "id": "OFFLINE-001",
        "name": "Password reset",
        "question": "How can I reset my password?",
        "expected_category": "it_access",
        "expected_answer_keywords": ["password"],
    }


def test_valid_response_passes(
    valid_response,
    valid_test_case,
):
    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is True


@pytest.mark.parametrize(
    ("mutation", "description"),
    [
        (
            lambda response: response.update(
                {"answer": ""}
            ),
            "empty answer",
        ),
        (
            lambda response: response.update(
                {"category": "hr"}
            ),
            "incorrect category",
        ),
        (
            lambda response: response.update(
                {"escalate": "false"}
            ),
            "invalid escalation type",
        ),
        (
            lambda response: response.update(
                {"session_id": ""}
            ),
            "empty session ID",
        ),
        (
            lambda response: response["usage"].update(
                {"input_tokens": True}
            ),
            "boolean token count",
        ),
        (
            lambda response: response["usage"].update(
                {"latency_ms": -1}
            ),
            "negative latency",
        ),
        (
            lambda response: response["meta"].update(
                {"model": ""}
            ),
            "empty model name",
        ),
    ],
    ids=[
        "empty-answer",
        "incorrect-category",
        "invalid-escalation-type",
        "empty-session-id",
        "boolean-token-count",
        "negative-latency",
        "empty-model",
    ],
)
def test_invalid_response_fails(
    valid_response,
    valid_test_case,
    mutation,
    description,
):
    mutation(valid_response)

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False, (
        f"Expected evaluation to fail for: {description}"
    )


@pytest.mark.parametrize(
    "invalid_response",
    [
        None,
        [],
        "not a response",
        {"answer": None},
    ],
    ids=[
        "none-response",
        "list-response",
        "string-response",
        "null-answer",
    ],
)
def test_malformed_response_does_not_crash(
    invalid_response,
    valid_test_case,
):
    result = evaluate_response(
        invalid_response,
        valid_test_case,
    )

    assert result["passed"] is False


def test_empty_expected_keywords_are_not_accepted(
    valid_response,
    valid_test_case,
):
    valid_test_case["expected_answer_keywords"] = []

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False

def test_missing_required_field_fails(
    valid_response,
    valid_test_case,
):
    del valid_response["category"]

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False
    assert result["checks"]["response_structure"] is False
    assert "category" in result["details"]["response_structure"]["reason"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("input_tokens", -1),
        ("output_tokens", "15"),
        ("latency_ms", 1.5),
    ],
    ids=[
        "negative-input-tokens",
        "string-output-tokens",
        "fractional-latency",
    ],
)
def test_invalid_usage_metrics_fail(
    valid_response,
    valid_test_case,
    field,
    value,
):
    valid_response["usage"][field] = value

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False
    assert result["checks"]["usage_metrics_present"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("input_tokens", None),
        ("output_tokens", None),
        ("latency_ms", None),
    ],
    ids=[
        "missing-input-tokens",
        "missing-output-tokens",
        "missing-latency",
    ],
)
def test_missing_usage_metrics_fail(
    valid_response,
    valid_test_case,
    field,
    value,
):
    del valid_response["usage"][field]

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False
    assert result["checks"]["usage_metrics_present"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model", ""),
        ("model", None),
        ("prompt_version", ""),
        ("prompt_version", None),
    ],
    ids=[
        "empty-model",
        "null-model",
        "empty-prompt-version",
        "null-prompt-version",
    ],
)
def test_invalid_model_metadata_fails(
    valid_response,
    valid_test_case,
    field,
    value,
):
    valid_response["meta"][field] = value

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False
    assert result["checks"]["model_metadata_present"] is False


def test_missing_expected_keyword_is_explained(
    valid_response,
    valid_test_case,
):
    valid_test_case["expected_answer_keywords"] = [
        "password",
        "refund",
    ]

    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is False
    assert result["checks"]["expected_answer_keywords"] is False
    assert "refund" in result["details"]["expected_answer_keywords"]["reason"]


def test_diagnostic_details_exist_for_every_check(
    valid_response,
    valid_test_case,
):
    result = evaluate_response(
        valid_response,
        valid_test_case,
    )

    assert result["passed"] is True
    assert set(result["details"]) == set(result["checks"])

    for check_name, passed in result["checks"].items():
        assert result["details"][check_name]["passed"] is passed
        assert isinstance(
            result["details"][check_name]["reason"],
            str,
        )
        assert result["details"][check_name]["reason"]