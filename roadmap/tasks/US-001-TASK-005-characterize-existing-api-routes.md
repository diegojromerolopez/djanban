# Task: Characterize existing API routes

- **ID**: `US-001-TASK-005`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FEATURE`
- **Depends On**: `US-001-TASK-001`, `US-001-TASK-002`
- **Target Files**: `djanban/api/boards.py`, `djanban/api/cards.py`, `djanban/api/lists.py`, `djanban/api/members.py`, `tests/characterization/test_api.py`, `djanban/urls.py`

## Description

Observe board, card, list, and member API routes before changing them. Mount only required compatibility adapters. Assert methods, paths, parameters, envelopes, types, pagination, content types, authentication, malformed JSON, extra fields, and error responses.
