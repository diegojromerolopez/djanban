# Task: Run quality gates and complete verification matrix

- **ID**: `US-001-TASK-006`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FIX`
- **Depends On**: `US-001-TASK-003`, `US-001-TASK-004`, `US-001-TASK-005`
- **Target Files**: `pyproject.toml`, `manage.py`, `djanban/settings.py`, `tests/conftest.py`, `tests/unit/test_health.py`, `tests/integration/test_health_endpoint.py`

## Description

Configure Ruff, strict mypy, pytest, and Django settings. Remove stubs, forbidden imports, real-time calls, network calls, and error masking. Run every verification command and automate all remaining scenario rows.
