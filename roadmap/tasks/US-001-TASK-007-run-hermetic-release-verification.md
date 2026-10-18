# Task: Run hermetic release verification

- **ID**: `US-001-TASK-007`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FIX`
- **Depends On**: `US-001-TASK-006`
- **Target Files**: `pyproject.toml`, `manage.py`, `tests/integration/test_health_endpoint.py`, `tests/characterization/test_boards.py`, `tests/characterization/test_cards.py`, `tests/characterization/test_lists.py`, `tests/characterization/test_authentication.py`, `tests/characterization/test_api.py`

## Description

Run all required commands inside a local uv environment. Verify every scenario row, exact command output, zero failures, and no analytics implementation.
