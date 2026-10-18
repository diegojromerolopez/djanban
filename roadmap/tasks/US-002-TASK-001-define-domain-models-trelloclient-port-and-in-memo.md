# Task: Define domain models, TrelloClient port, and in-memory test double

- **ID**: `US-002-TASK-001`
- **Story ID**: `US-002`
- **Status**: `PENDING`
- **Change Type**: `FEATURE`
- **Depends On**: `US-001-TASK-001`
- **Target Files**: `src/djanban/domain/__init__.py`, `src/djanban/domain/models.py`, `src/djanban/domain/ports.py`, `tests/doubles/in_memory_trello_client.py`, `tests/unit/domain/test_models.py`

## Description

Create typed domain dataclasses for lists, cards, transitions, and WIP limits. Define the TrelloClient protocol in ports. Implement InMemoryTrelloClient and co-located unit tests.
