# NexaDesk Evaluation Framework

A standalone framework for testing and evaluating the quality and reliability
of LLM-powered applications.

## Purpose

This repository contains evaluation code for the NexaDesk V1 application.
The application under test is maintained separately in the `nexadesk-v1`
repository.

## Architecture

- Application under test: NexaDesk V1
- Evaluation framework: this repository
- Application communication: HTTP API
- Initial execution environment: Python 3.11

## Prerequisites

- Python 3.11
- NexaDesk V1 running locally
- Git

## Setup

Create and activate a virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate