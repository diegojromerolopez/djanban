# djanban Modernization Specification

## 1. Goal

Modernize djanban for Python 3.12 or later and Django 5.x. Preserve existing supported behavior through characterization tests. Replace the AngularJS client with Django REST API endpoints and optional Django templates.

## 2. Required Toolchain

Use Python 3.12 or later. Use Django 5.x. Use pytest, pytest-django, ruff, and mypy. Use SQLite for local and integration tests. Run all unit and integration tests without network access.

Required commands:

```text
python -m pytest
ruff check .
python -m mypy --strict .
python manage.py check
```

All commands must return exit code 0 on success. A failing test, lint error, type error, or Django check must return a non-zero exit code.

## 3. Architecture

Keep pure domain models and calculators in `djanban/domain/`. Do not import Django ORM classes from domain modules. Inject a `TrelloClient` protocol into application services. Tests must use fake clients or in-memory repositories.

Use these modules:

```text
djanban/domain/models.py
djanban/domain/wip.py
djanban/domain/regressions.py
djanban/domain/time_tracking.py
djanban/domain/lead_cycle.py
djanban/domain/schedule.py
djanban/api/serializers.py
djanban/api/views/wip.py
djanban/api/views/regressions.py
djanban/api/views/time_tracking.py
djanban/api/views/lead_cycle.py
djanban/api/views/schedule.py
djanban/api/views/boards.py
djanban/api/views/cards.py
djanban/api/views/lists.py
djanban/api/urls.py
djanban/settings.py
manage.py
```

Remove AngularJS application assets from the active web application. Do not add new AngularJS code.

## 4. Authentication and HTTP Rules

Require an authenticated Django user for every `/api/v1/` endpoint. Support Django session authentication and token authentication when configured. Return HTTP 401 for missing authentication and HTTP 403 for authenticated users without board access. Apply CSRF protection to session-authenticated unsafe requests.

Return JSON with `Content-Type: application/json`. Return HTTP 404 when a board does not exist or the user cannot access it. Return HTTP 400 for invalid query parameters or invalid stored data. Use this error shape:

```json
{"error":{"code":"INVALID_REQUEST","message":"..."}}
```

Use stable uppercase error codes. Do not expose secrets or stack traces.

## 5. Trello Data Contract

Define a typed `TrelloClient` protocol with read operations for boards, lists, cards, members, comments, and card movements. The application may read synchronized local data or an injected client. No endpoint may call the live Trello service during tests.

A list has `list_id`, `list_name`, `workflow_order`, `min_wip`, `max_wip`, and `is_done`. A card has `card_id`, `title`, `list_id`, `created_at`, assigned member IDs, comments, and ordered movement events. A movement has `occurred_at`, `from_list_id`, and `to_list_id`. A comment has author member ID, text, and timestamp.

Use timezone-aware UTC datetimes. Reject naive timestamps in domain input with `INVALID_DATA`.

## 6. WIP Endpoint

Implement `GET /api/v1/boards/{board_id}/wip-status`.

Return HTTP 200 with:

```json
{
  "board_id":"b-101",
  "lists":[
    {
      "list_id":"l-in-progress",
      "list_name":"In Progress",
      "card_count":5,
      "max_wip":3,
      "status":"OVER_WIP"
    }
  ]
}
```

Allowed statuses are `UNDER_WIP`, `AT_WIP`, `OVER_WIP`, and `NO_LIMIT`. A missing minimum or maximum disables that boundary. Treat an absent minimum and maximum as `NO_LIMIT`. Reject negative thresholds. Count current cards only.

## 7. Regression Endpoint

Implement `GET /api/v1/boards/{board_id}/regressions`.

Order lists by `workflow_order`. Record a regression when a movement goes from a higher order to a lower order. Count total regressions, per-card regressions, and per-list destination regressions. Calculate `regression_rate` as `total_regressions / total_transitions`. Return `0.0` when there are no transitions. Round rates to four decimal places.

Return HTTP 200 with:

```json
{
  "board_id":"b-101",
  "total_regressions":4,
  "regression_rate":0.12,
  "regressed_cards":[
    {
      "card_id":"c-42",
      "title":"Fix authentication bug",
      "regression_count":2,
      "last_regression_from":"Testing",
      "last_regression_to":"In Progress"
    }
  ]
}
```

Sort cards by descending regression count, then card ID. Ignore movements with unknown lists and return `INVALID_DATA` when stored movement data is malformed.

## 8. Time Tracking Endpoint

Implement `GET /api/v1/boards/{board_id}/time-tracking`.

Parse Plus for Trello entries matching the complete comment token `(spent/estimated)`. Permit decimal values with a period and surrounding whitespace. Reject negative values. Ignore comments without a valid token. Aggregate spent and estimated hours by card, list, board, and member. Attribute a comment to its author member. Round all hour values to two decimal places using decimal arithmetic and half-up rounding.

Return HTTP 200 with:

```json
{
  "board_id":"b-101",
  "total_spent_hours":42.5,
  "total_estimated_hours":50.0,
  "member_workload":[
    {
      "member_id":"m-alice",
      "name":"Alice Smith",
      "spent_hours":24.0,
      "estimated_hours":28.0
    }
  ]
}
```

Return zero totals for an empty board. Do not produce negative, NaN, or infinite values.

## 9. Lead and Cycle Endpoint

Implement `GET /api/v1/boards/{board_id}/lead-cycle-times`.

Lead time is the duration from card creation to the first entry into a list marked `is_done`. Cycle time is the duration spent in lists that are neither backlog nor done. Identify backlog lists by `is_backlog`; treat an active list as neither backlog nor done. Use completed cards only for metrics. Return durations in days, rounded to two decimal places.

Return average, median, minimum, and maximum lead and cycle times. Return `null` for each statistic when no completed cards exist. Return HTTP 400 with `INVALID_DATA` for reversed or missing required timestamps.

The response fields are:

```json
{
  "board_id":"b-101",
  "avg_lead_time_days":4.5,
  "median_lead_time_days":3.8,
  "min_lead_time_days":1.2,
  "max_lead_time_days":8.0,
  "avg_cycle_time_days":2.1,
  "median_cycle_time_days":1.9,
  "min_cycle_time_days":0.5,
  "max_cycle_time_days":4.0
}
```

## 10. Schedule Endpoint

Implement `GET /api/v1/boards/{board_id}/schedule-status`.

Calculate `completion_percentage` as completed estimated hours divided by total estimated hours times 100. Calculate `time_spent_percentage` as total spent hours divided by total estimated hours times 100. Set `status` to `ON_TIME` when completion is greater than or equal to time spent minus 5. Otherwise set `BEHIND_SCHEDULE`.

Return HTTP 200 with:

```json
{
  "board_id":"b-101",
  "completion_percentage":75.0,
  "time_spent_percentage":85.0,
  "status":"BEHIND_SCHEDULE"
}
```

Round percentages to two decimal places. Return `NO_ESTIMATE` with both percentages set to `0.0` when total estimated hours equal zero. Reject negative hours.

## 11. Management APIs

Expose authenticated CRUD endpoints under `/api/v1/boards/`, `/api/v1/boards/{board_id}/lists/`, and `/api/v1/boards/{board_id}/cards/`. Support GET collection, GET detail, POST, PATCH, and DELETE where the legacy behavior supports the operation. Return 200 for successful reads and updates, 201 for creation, 204 for deletion, 400 for validation errors, 401 for missing authentication, 403 for access denial, and 404 for missing resources.

Use explicit serializers. Validate required IDs, names, workflow order, thresholds, timestamps, and foreign-key ownership. Return the standard error envelope.

## 12. Testing

Create characterization tests before changing legacy behavior. Create pure unit tests for every calculator and parser. Create Django integration tests with an in-memory SQLite database. Use fake Trello clients, in-memory repositories, and deterministic clocks. Do not call Trello or any external network service in tests.

Test empty inputs, missing limits, boundary thresholds, zero transitions, malformed comments, decimal precision, duplicate movements, unknown lists, missing estimates, inaccessible boards, invalid JSON, authentication failures, CSRF failures, and all documented HTTP status codes.

## 13. Required Artifacts

Provide `manage.py`, `pyproject.toml`, `djanban/settings.py`, `djanban/domain/`, `djanban/api/`, and `tests/`. Configure pytest-django, ruff, and strict mypy. Keep the active application free from AngularJS dependencies.

## 14. Completion Criteria

The modernization is complete only when all endpoint contracts work, characterization tests pass, new unit and integration tests pass, `python -m pytest` returns zero, `ruff check .` returns zero, `python -m mypy --strict .` returns zero, and `python manage.py check` returns zero.