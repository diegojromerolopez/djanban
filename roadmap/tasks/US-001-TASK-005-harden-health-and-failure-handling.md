# Task: Harden health and failure handling

- **ID**: `US-001-TASK-005`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FIX`
- **Depends On**: `US-001-TASK-001`
- **Target Files**: `manage.py`, `djanban/settings.py`, `djanban/urls.py`, `djanban/health.py`, `tests/unit/test_health.py`, `tests/integration/test_health_endpoint.py`

## Description

Complete health negative cases and command failure handling. Verify exact JSON, headers, 404, 405, no traces, missing settings, and the required error prefix.
