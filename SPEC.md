# SPEC.md: djanban (Legacy Django Kanban Analytics Modernization)

## 1. Executive Summary

`djanban` is a Kanban metrics, statistics, and analytics platform that connects to Trello board data to compute strategic project management metrics (Work In Progress limits, Lead/Cycle time, team time tracking, task flow regressions, and project completion status).

> [!IMPORTANT]
> **Legacy Codebase Modernization Directive**:
> The original codebase was built using obsolete versions of Python (2.7/3.4) and Django 1.x, along with a legacy AngularJS client interface.
> 
> As part of this dark factory project:
> 1. **Upgrade**: The project MUST be modernized to run on **Python 3.12+** and **Django 5.x**.
> 2. **Frontend Simplification**: The legacy AngularJS frontend is **deprecated and removed**. The web application must be exposed via clean, typed Django REST API endpoints (`/api/v1/...`) and/or modern server-side Django HTML templates.
> 3. **Toolchain Gates**: The modernized code must pass strict static analysis (`ruff check .`, `mypy --strict`) and unit/integration tests (`pytest`).

---

## 2. Strategic Management Questions & Domain Invariants

The modernized system must directly answer the 5 core strategic management questions outlined in `djanban`'s original design, backed by concrete JSON wire contracts and pure domain calculators:

### 2.1 Question 1: "Is the maximum Work In Progress (WIP) for each state/list being followed?"
* **Domain Component**: `WIPCalculator`
* **Rules**:
  * Each board list can have optional `min_wip` and `max_wip` thresholds.
  * `WIPStatus` computes whether `current_card_count` falls within `[min_wip, max_wip]`.
  * Flags `OVER_WIP` when `card_count > max_wip` and `UNDER_WIP` when `card_count < min_wip`.
* **API Endpoint**: `GET /api/v1/boards/{board_id}/wip-status`
* **JSON Wire Contract**:
  ```json
  {
    "board_id": "b-101",
    "lists": [
      {
        "list_id": "l-in-progress",
        "list_name": "In Progress",
        "card_count": 5,
        "max_wip": 3,
        "status": "OVER_WIP"
      }
    ]
  }
  ```

---

### 2.2 Question 2: "Are tasks going back to earlier states too much (workflow regressions)?"
* **Domain Component**: `RegressionTracker`
* **Rules**:
  * Lists are ordered sequentially by workflow order (e.g. `1: Backlog`, `2: In Progress`, `3: Testing`, `4: Done`).
  * A **Regression** occurs whenever a card transitions from a list of higher order to a list of lower order (e.g. `Testing` $\rightarrow$ `In Progress`).
  * Records regression count per card, per list, and overall board regression rate (`total_regressions / total_transitions`).
* **API Endpoint**: `GET /api/v1/boards/{board_id}/regressions`
* **JSON Wire Contract**:
  ```json
  {
    "board_id": "b-101",
    "total_regressions": 4,
    "regression_rate": 0.12,
    "regressed_cards": [
      {
        "card_id": "c-42",
        "title": "Fix authentication bug",
        "regression_count": 2,
        "last_regression_from": "Testing",
        "last_regression_to": "In Progress"
      }
    ]
  }
  ```

---

### 2.3 Question 3: "How many hours are your team working and in what projects?"
* **Domain Component**: `PlusForTrelloParser` & `TimeTracker`
* **Rules**:
  * Parses card comments following the **Plus for Trello** comment syntax: `(spent/estimated)` e.g., `(2.5/4.0)` = 2.5 hours spent, 4.0 estimated.
  * Aggregates total spent hours and total estimated hours per card, per list, per board, and per team member (`member_id`).
  * Number precision invariant: All calculated hours rounded to 2 decimal places.
* **API Endpoint**: `GET /api/v1/boards/{board_id}/time-tracking`
* **JSON Wire Contract**:
  ```json
  {
    "board_id": "b-101",
    "total_spent_hours": 42.50,
    "total_estimated_hours": 50.00,
    "member_workload": [
      {
        "member_id": "m-alice",
        "name": "Alice Smith",
        "spent_hours": 24.00,
        "estimated_hours": 28.00
      }
    ]
  }
  ```

---

### 2.4 Question 4: "What's the Lead Time and Cycle Time of each project's tasks?"
* **Domain Component**: `LeadCycleCalculator`
* **Definitions**:
  * **Lead Time**: Time duration (in hours/days) from card creation until entry into a `Done` list.
  * **Cycle Time**: Time duration (in hours/days) spent in active work lists (excluding `Backlog` and `Done`).
* **Rules**:
  * Computes average, median, minimum, and maximum Lead/Cycle times per board.
* **API Endpoint**: `GET /api/v1/boards/{board_id}/lead-cycle-times`
* **JSON Wire Contract**:
  ```json
  {
    "board_id": "b-101",
    "avg_lead_time_days": 4.50,
    "median_lead_time_days": 3.80,
    "avg_cycle_time_days": 2.10,
    "median_cycle_time_days": 1.90
  }
  ```

---

### 2.5 Question 5: "Is the project on time according to its percentage of completion?"
* **Domain Component**: `ScheduleAnalyzer`
* **Rules**:
  * `completion_percentage`: `(completed_estimated_hours / total_estimated_hours) * 100`.
  * `time_spent_percentage`: `(total_spent_hours / total_estimated_hours) * 100`.
  * Status is `ON_TIME` if `completion_percentage >= time_spent_percentage - 5%`, otherwise `BEHIND_SCHEDULE`.
* **API Endpoint**: `GET /api/v1/boards/{board_id}/schedule-status`
* **JSON Wire Contract**:
  ```json
  {
    "board_id": "b-101",
    "completion_percentage": 75.00,
    "time_spent_percentage": 85.00,
    "status": "BEHIND_SCHEDULE"
  }
  ```

---

## 3. Architecture & Mandatory Engineering Directives

1. **Language & Framework**: Python 3.12+, Django 5.x.
2. **SOLID & DDD Principles**:
   - Single-responsibility domain services (`WIPCalculator`, `RegressionTracker`, `PlusForTrelloParser`, `LeadCycleCalculator`, `ScheduleAnalyzer`) decoupled from Django HTTP handlers.
   - Pure Python domain models with zero dependencies on Django ORM for calculation logic.
3. **Dependency Injection**:
   - `TrelloClient` protocol interface provided via constructor dependency injection.
   - Unit tests MUST use fake/mock `TrelloClient` data and run 100% offline without network calls.
4. **Testing Strategy**:
   - **Unit Tests**: Test time parsing, WIP math, Lead/Cycle calculations, and schedule status using fake domain objects.
   - **Integration Tests**: Test Django REST endpoints (`/api/v1/...`) against an in-memory SQLite database using `pytest-django`.
5. **Quality & Linter Gates**:
   - Zero errors on `ruff check .`
   - Zero errors on `mypy --strict .`
   - 100% pass on `pytest` / `python manage.py test`

---

## 4. Required File Artifacts

The modernized repository MUST produce at minimum:
- `manage.py`: Django 5.x management script.
- `pyproject.toml`: Modern Python project specification with dependencies (`django>=5.0`, `pytest-django`, `ruff`, `mypy`).
- `djanban/settings.py`: Clean Django settings file.
- `djanban/domain/`: Pure domain calculators and value objects (WIP, time tracking, Lead/Cycle math).
- `djanban/api/`: Django REST API views and serializers mapping to `/api/v1/...`.
- `tests/`: Unit and integration test suite.


## 5. Definition of Done (DoD)

To consider `djanban` fully modernized and operational, the codebase must satisfy:
1. **Public API & Web Interfaces:** All Django endpoints and UI views for board/card/column management execute correctly with proper HTTP status codes, CSRF handling, and authentication.
2. **Linting Invariant:** Zero static analysis errors or warnings under `ruff check . && mypy --strict .`.
3. **Verification Criteria:** 100% test pass rate executing `pytest`.
