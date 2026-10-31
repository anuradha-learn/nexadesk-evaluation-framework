import json
from pathlib import Path

import pytest

from evaluation.client import send_chat
from evaluation.evaluators import evaluate_response


DATASET_PATH = (
    Path(__file__).resolve().parents[1]
    / "evaluation"
    / "datasets"
    / "chat_cases.json"
)

with DATASET_PATH.open(encoding="utf-8") as file:
    TEST_CASES = json.load(file)

@pytest.mark.live

@pytest.mark.parametrize(
    "test_case",
    TEST_CASES,
    ids=lambda case: case["id"],
)
def test_chat_evaluation(test_case):
    """Evaluate a NexaDesk response against a dataset case."""

    response = send_chat(test_case["question"])
    result = evaluate_response(response, test_case)

    print(f"\nTest case: {result['test_case_id']}")
    print(f"Name: {result['test_case_name']}")

    for check_name, passed in result["checks"].items():
        print(f"{check_name}: {'PASS' if passed else 'FAIL'}")

    assert result["passed"], (
        f"Evaluation failed for {result['test_case_id']}: "
        f"{result['checks']}"
    )