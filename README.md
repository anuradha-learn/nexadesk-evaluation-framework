# NexaDesk Evaluation Framework

A standalone Python framework for evaluating the quality, correctness, and reliability of LLM-powered applications.

This repository contains the evaluation framework for **NexaDesk V1**. The application under test is maintained separately in the `nexadesk-v1` repository.

## Purpose

The goal is to build a practical, reusable framework for evaluating an LLM-powered application through its HTTP API.

The framework separates the application from the evaluation logic so that responses can be tested against predefined expectations.

## Architecture

The initial evaluation workflow is:

1. Load test cases from a JSON dataset.
2. Send a test question to NexaDesk through its HTTP API.
3. Receive the JSON response.
4. Evaluate the response against the expected results.
5. Report individual check results and an overall pass/fail status.

### Components

| Component | Responsibility |
|---|---|
| `evaluation/datasets/chat_cases.json` | Stores test cases and expected results |
| `evaluation/client.py` | Sends requests to the NexaDesk API |
| `evaluation/evaluators.py` | Evaluates responses and generates diagnostic details |
| `tests/test_evaluators.py` | Tests evaluator behavior offline |
| `tests/test_chat_evaluation.py` | Evaluates actual responses from NexaDesk |

## Prerequisites

- Python 3.11
- Git
- NexaDesk V1 running locally for live evaluations

**Important:** Offline evaluator tests do not require NexaDesk to be running and do not make LLM calls.

Live evaluations require a running NexaDesk instance. Depending on the application's configuration, they may incur LLM API costs.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/anuradha-learn/nexadesk-evaluation-framework.git
cd nexadesk-evaluation-framework
```

### 2. Create and activate a virtual environment

On macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Configuration

By default, the evaluation client connects to:

```text
http://localhost:8001
```

To use a different NexaDesk URL, set the `NEXADESK_BASE_URL` environment variable before running the tests.

For example:

```bash
export NEXADESK_BASE_URL="http://localhost:8001"
```

The evaluation framework expects NexaDesk to expose a compatible `/chat` HTTP endpoint.

## Running Tests

### 1. Run offline evaluator tests

These tests validate the evaluation logic using predefined test data. They do not call NexaDesk or an LLM.

```bash
python -m pytest tests/test_evaluators.py -v
```

### 2. Run all offline tests

The `live` marker identifies tests that call the NexaDesk API.

To run tests excluding live evaluations:

```bash
python -m pytest -m "not live" -v
```

This is the recommended command for routine development because it avoids accidentally triggering live evaluations.

### 3. Collect live tests without executing them

To see which tests are marked as live:

```bash
python -m pytest --collect-only -m live -q
```

This command discovers tests but does not execute them or make API calls.

### 4. Run live evaluations

**Run this command only when you intentionally want to evaluate actual NexaDesk responses.**

Make sure NexaDesk V1 is running and its endpoint is configured correctly.

```bash
python -m pytest -m live -v
```

Live evaluations send real requests to NexaDesk and may incur LLM costs.

## Test Dataset

The initial dataset is stored in:

```text
evaluation/datasets/chat_cases.json
```

Each test case includes:

- `id`: Unique test case identifier
- `name`: Descriptive test case name
- `question`: Question sent to NexaDesk
- `expected_category`: Expected response category
- `expected_answer_keywords`: Keywords expected in the generated answer

Example:

```json
{
  "id": "CHAT-001",
  "name": "Password reset",
  "question": "How can I reset my Nexa Group account password?",
  "expected_category": "it_access",
  "expected_answer_keywords": [
    "password"
  ]
}
```

## Evaluation Checks

The initial evaluator checks:

- Response structure and required fields
- Non-empty answer
- Expected response category
- Expected answer keywords
- Boolean escalation flag
- Non-empty session ID
- Valid usage metrics
- Model and prompt-version metadata

Each check produces a Boolean result and a diagnostic explanation.

A test case passes only when all evaluator checks pass.

## Current Scope

The initial implementation focuses on deterministic response checks and reliable test execution.

It does not yet provide comprehensive semantic evaluation of answer correctness, automated regression comparisons, or production-scale evaluation reporting.

These capabilities can be introduced as the framework evolves.

## Repository Structure

```text
nexadesk-evaluation-framework/
├── evaluation/
│   ├── client.py
│   ├── evaluators.py
│   └── datasets/
│       └── chat_cases.json
├── tests/
│   ├── test_evaluators.py
│   └── test_chat_evaluation.py
├── pytest.ini
├── requirements.txt
└── README.md
```