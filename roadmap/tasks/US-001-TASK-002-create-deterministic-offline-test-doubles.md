# Task: Create deterministic offline test doubles

- **ID**: `US-001-TASK-002`
- **Story ID**: `US-001`
- **Status**: `PENDING`
- **Change Type**: `FEATURE`
- **Depends On**: `US-001-TASK-001`
- **Target Files**: `tests/doubles/fake_trello_client.py`, `tests/doubles/fake_clock.py`, `tests/unit/test_fake_trello_client.py`, `tests/unit/test_fake_clock.py`, `tests/conftest.py`

## Description

Implement in-memory Trello and clock doubles. Store boards, lists, cards, and members. Raise explicit errors for unknown identifiers. Add tests for deterministic reads, writes, and selected instants.
