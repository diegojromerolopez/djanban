# Task: Apply static quality gates

- **ID**: `US-001-TASK-006`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FIX`
- **Depends On**: `US-001-TASK-002`, `US-001-TASK-003`, `US-001-TASK-004`, `US-001-TASK-005`
- **Target Files**: `pyproject.toml`, `djanban/settings.py`, `djanban/domain/__init__.py`, `djanban/api/__init__.py`, `tests/conftest.py`, `tests/test_project_configuration.py`

## Description

Configure Ruff, strict mypy, pytest, and in-memory SQLite. Remove stubs, broad masking, network calls, and facade imports. Add focused configuration tests.
