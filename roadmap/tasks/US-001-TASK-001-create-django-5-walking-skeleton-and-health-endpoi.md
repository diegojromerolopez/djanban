# Task: Create Django 5 walking skeleton and health endpoint

- **ID**: `US-001-TASK-001`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FEATURE`
- **Depends On**: `[]` 
- **Target Files**: `manage.py`, `pyproject.toml`, `djanban/__init__.py`, `djanban/settings.py`, `djanban/urls.py`, `djanban/wsgi.py`, `djanban/health.py`, `djanban/domain/__init__.py`, `djanban/api/__init__.py`, `tests/conftest.py`, `tests/unit/test_health.py`, `tests/integration/test_health_endpoint.py`

## Description

Create the Django 5 project entrypoint. Configure Python 3.12, Django 5, pytest, ruff, and mypy in pyproject.toml. Implement the health endpoint. Write unit and integration tests for the health endpoint. Configure pytest to use in-memory SQLite. Keep manage.py under 15 executable lines. Do not use network calls.
