# Task: Characterize board and card behavior

- **ID**: `US-001-TASK-003`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FEATURE`
- **Depends On**: `US-001-TASK-001`, `US-001-TASK-002`
- **Target Files**: `djanban/legacy/boards.py`, `djanban/legacy/cards.py`, `tests/characterization/test_boards.py`, `tests/characterization/test_cards.py`

## Description

Observe legacy board and card routes before changing them. Add focused compatibility adapters only when the modern entrypoint requires them. Assert status codes, redirects, templates, JSON envelopes, fields, validation, ordering, permissions, and duplicate submissions.
