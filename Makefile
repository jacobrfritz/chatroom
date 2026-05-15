.PHONY: install test test-watch test-cov lint format typecheck run

install:
	uv sync

test:
	uv run pytest

test-watch:
	uv run ptw

test-cov:
	uv run pytest --cov=src --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy src

run:
	@trap 'kill 0' EXIT; uv run chatroom & python3 -m http.server 8080
