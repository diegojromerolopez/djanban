# US-004: Schedule Status and Management API

## Story

As an authenticated board member, I want schedule status and board management APIs, so that I can track delivery and manage work safely.

## Scope

Implement schedule status calculations and authenticated APIs for boards, cards, and lists.
Preserve legacy behavior with characterization tests from US-001.
Keep calculation logic independent from Django ORM classes.
Use Python 3.12+ and Django 5.x.

## Dependencies

- depends_on: [US-001]
- change_type: new
- complexity: 32 CU
- domain_slice: Schedule Analysis, Board Management, Card Management, and List Management

## Observable Entry Point

Use the Django entrypoint at `src/manage.py`.

Run the test suite with `python3.12 src/manage.py test`.
Run the modern suite with `pytest -q`.
Run static checks with `ruff check .` and `mypy --strict .`.
Start the local server with `python3.12 src/manage.py runserver 127.0.0.1:8000`.

The HTTP interface uses TCP and HTTP/1.1.
The base path is `/api/v1`.
The API returns JSON with UTF-8 encoding.
The API does not call external networks during tests.

Successful commands exit with status `0`.
Command failures exit with a non-zero status.
Pytest must print `0 failed` before it exits successfully.
Ruff and mypy must print no error line.
Django command errors must start with `CommandError:` on stderr.

## Authentication Contract

Require authentication for every endpoint in this story.
Accept a valid Django session or `Authorization: Bearer <token>` header.
Return `401` when credentials are absent or invalid.
Return `403` when the member lacks board access.
Do not reveal board existence to an unauthorised member.

Return this JSON error envelope for HTTP errors:

    {"error":{"code":"AUTHENTICATION_REQUIRED","message":"Authentication is required."}}

Use these error codes:

- `AUTHENTICATION_REQUIRED`
- `PERMISSION_DENIED`
- `BOARD_NOT_FOUND`
- `CARD_NOT_FOUND`
- `LIST_NOT_FOUND`
- `INVALID_JSON`
- `VALIDATION_ERROR`
- `CONFLICT`
- `METHOD_NOT_ALLOWED`
- `SCHEDULE_DATA_INVALID`

The `message` field must contain one stable, plain-English sentence.
Validation responses must include `field_errors` when a field causes the error.

## Schedule Status API

Implement `GET /api/v1/boards/{board_id}/schedule-status`.

Return `200` with this exact envelope:

    {"board_id":"b-101","completion_percentage":75.00,"time_spent_percentage":85.00,"status":"BEHIND_SCHEDULE"}

Calculate completion as completed estimated hours divided by total estimated hours.
Calculate time spent as total spent hours divided by total estimated hours.
Multiply both values by 100.
Set `ON_TIME` when completion is at least time spent minus five percentage points.
Set `BEHIND_SCHEDULE` otherwise.
Round percentages to exactly two decimal places in JSON numbers.
Use decimal arithmetic, not binary floating-point arithmetic.
Reject a zero or negative total estimate with status `422`.
Return `SCHEDULE_DATA_INVALID` for that condition.
Treat zero spent hours as valid input.
Allow completion above 100 percent when completed estimates exceed the total estimate.
Reject negative spent or estimated hours.

## Board Management API

Implement these authenticated endpoints:

- `GET /api/v1/boards`
- `POST /api/v1/boards`
- `GET /api/v1/boards/{board_id}`
- `PATCH /api/v1/boards/{board_id}`
- `DELETE /api/v1/boards/{board_id}`

Return `200` for successful reads and updates.
Return `201` for successful creation.
Return `204` for successful deletion with an empty body.
Return `404` with the matching not-found code for an accessible missing resource.
Return `409` when deletion violates an active dependency.

Accept this creation body:

    {"name":"Delivery Board","description":"Release work"}

Require a non-empty `name` with at most 200 Unicode characters.
Allow a missing or null `description` and store it as an empty string.
Limit `description` to 2000 Unicode characters.
Reject unknown fields with `VALIDATION_ERROR`.
Return a stable board object with `id`, `name`, `description`, `created_at`, and `updated_at`.
Serialize timestamps as UTC ISO 8601 strings ending in `Z`.

Allow `PATCH` to change `name` and `description` only.
Reject an empty patch body.
Do not allow a member to change another member's board.

## List Management API

Implement these authenticated endpoints:

- `GET /api/v1/boards/{board_id}/lists`
- `POST /api/v1/boards/{board_id}/lists`
- `GET /api/v1/boards/{board_id}/lists/{list_id}`
- `PATCH /api/v1/boards/{board_id}/lists/{list_id}`
- `DELETE /api/v1/boards/{board_id}/lists/{list_id}`

Accept this creation body:

    {"name":"In Progress","position":2,"min_wip":1,"max_wip":5}

Require a non-empty `name` with at most 200 Unicode characters.
Require an integer `position` greater than or equal to zero.
Allow null `min_wip` and `max_wip` to disable a threshold.
Require integer thresholds greater than or equal to zero.
Require `min_wip` to be no greater than `max_wip` when both exist.
Reject decimal, boolean, negative, and string threshold values.
Return list objects with `id`, `board_id`, `name`, `position`, `min_wip`, and `max_wip`.
Order list collections by ascending position and then ascending identifier.

## Card Management API

Implement these authenticated endpoints:

- `GET /api/v1/boards/{board_id}/cards`
- `POST /api/v1/boards/{board_id}/cards`
- `GET /api/v1/boards/{board_id}/cards/{card_id}`
- `PATCH /api/v1/boards/{board_id}/cards/{card_id}`
- `DELETE /api/v1/boards/{board_id}/cards/{card_id}`

Accept this creation body:

    {"title":"Fix authentication bug","description":"Repair token flow","list_id":"l-1","estimated_hours":4.00}

Require a non-empty `title` with at most 500 Unicode characters.
Limit `description` to 10000 Unicode characters.
Require an existing list that belongs to the selected board.
Allow `estimated_hours` to be null or a non-negative decimal.
Serialize hours with exactly two decimal places.
Reject negative, NaN, infinity, boolean, and malformed numeric values.
Return card objects with `id`, `board_id`, `list_id`, `title`, `description`, `estimated_hours`, `spent_hours`, `created_at`, and `updated_at`.

When a card changes lists, record one ordered movement event.
Reject a list from another board with `VALIDATION_ERROR`.
Preserve movement history when a card is updated.

## Schedule Domain Component

Create `ScheduleAnalyzer` as a pure Python service.
Pass typed domain values into its constructor or calculation method.
Do not import Django models, views, or serializers into the domain module.
Return a typed result with decimal percentages and a status enum.
Raise a typed validation error for invalid totals or negative values.

Use an injected `TrelloClient` protocol for external board data.
Provide an in-memory fake client for all unit and integration tests.
Never make a network request in a test.

## Required Repository Paths

Create or update these exact paths:

- `src/djanban/domain/schedule.py`
- `src/djanban/domain/schedule_models.py`
- `src/djanban/domain/exceptions.py`
- `src/djanban/integrations/trello_protocol.py`
- `src/djanban/integrations/in_memory_trello.py`
- `src/djanban/api/v1/boards.py`
- `src/djanban/api/v1/cards.py`
- `src/djanban/api/v1/lists.py`
- `src/djanban/api/v1/schedule.py`
- `src/djanban/api/v1/serializers.py`
- `src/djanban/api/v1/errors.py`
- `src/djanban/api/v1/urls.py`
- `src/djanban/apps/boards/models.py`
- `src/djanban/apps/boards/migrations/0001_initial.py`
- `src/djanban/apps/boards/admin.py`
- `src/djanban/urls.py`
- `tests/unit/domain/test_schedule.py`
- `tests/unit/integrations/test_in_memory_trello.py`
- `tests/integration/api/test_schedule_status.py`
- `tests/integration/api/test_board_management.py`
- `tests/integration/api/test_card_management.py`
- `tests/integration/api/test_list_management.py`
- `tests/integration/api/test_authentication.py`
- `tests/e2e/test_us004_http.py`
- `tests/characterization/test_legacy_board_management.py`
- `tests/characterization/test_legacy_card_management.py`
- `tests/characterization/test_legacy_list_management.py`

Keep handlers in their listed modules.
Do not import internal handlers from package facades or index modules.
Avoid circular imports by importing concrete modules directly.

## Scenario Matrix

| Case | Request or input | Expected result |
|---|---|---|
| Valid schedule | Total 100, completed 75, spent 85 | `200`, `75.00`, `85.00`, `BEHIND_SCHEDULE` |
| Five-point boundary | Completion equals spent minus 5 | `200`, `ON_TIME` |
| Ahead schedule | Completion exceeds spent | `200`, `ON_TIME` |
| Zero total | Total estimate is 0 | `422`, `SCHEDULE_DATA_INVALID` |
| Negative hours | Any negative hour value | `422`, `VALIDATION_ERROR` |
| Missing credentials | No session or bearer token | `401`, `AUTHENTICATION_REQUIRED` |
| Invalid credentials | Bad bearer token | `401`, `AUTHENTICATION_REQUIRED` |
| No board access | Valid member without access | `403`, `PERMISSION_DENIED` |
| Unknown board | Accessible path with unknown identifier | `404`, `BOARD_NOT_FOUND` |
| Duplicate or foreign list | Card uses another board's list | `422`, `VALIDATION_ERROR` |
| Empty name | Blank or whitespace-only name | `422`, `VALIDATION_ERROR` |
| Long name | More than 200 characters | `422`, `VALIDATION_ERROR` |
| Bad JSON | Truncated JSON body | `400`, `INVALID_JSON` |
| Unknown field | Body contains an unsupported field | `422`, `VALIDATION_ERROR` |
| Wrong method | Unsupported HTTP method | `405`, `METHOD_NOT_ALLOWED` |
| Missing card or list | Unknown child identifier | Matching `404` error |
| Card movement | Card changes to a board list | `200` and one movement event |
| Delete active board | Board has dependent protected data | `409`, `CONFLICT` |
| Empty collection | Board has no cards or lists | `200` with an empty array |

Test all matrix rows through HTTP.
Test malformed content types and oversized JSON bodies.
Test Unicode names and boundary-length values.
Test repeated updates for idempotent PATCH behavior.

## Testing Rules

Use Chicago-school tests with observable behavior and real module boundaries.
Use in-memory test doubles for Trello data and external services.
Use an in-memory SQLite database for integration tests.
Use a deterministic mock clock for every timestamp assertion.
Do not use static sleep delays in end-to-end tests.
Poll socket readiness until the configured timeout expires.
Fail the test when readiness does not occur.
Cover every scenario in the matrix with black-box HTTP tests.
Preserve and pass all US-001 characterization tests.
Do not weaken an assertion to make a legacy test pass.

## Anti-Stub and Negative Constraints

Do not add `pass`, ellipsis bodies, or `NotImplementedError`.
Do not add placeholder responses or fake success status codes.
Do not mask shell failures with `|| true`.
Do not use network calls in unit or integration tests.
Do not use floating-point arithmetic for schedule percentages.
Do not restore AngularJS dependencies.
Do not place calculation rules in Django HTTP handlers.
Do not expose unauthenticated management or schedule data.
Do not use static sleep delays for readiness.

## Definition of Done

- Implement every endpoint and response envelope in this story.
- Return the stated status code for every matrix case.
- Enforce authentication and board-level authorization.
- Persist board, card, list, and movement data safely.
- Preserve legacy behavior through characterization tests.
- Use deterministic clocks in all time assertions.
- Use in-memory doubles in domain and component tests.
- Pass 100 percent of unit tests.
- Pass 100 percent of integration tests.
- Pass 100 percent of black-box end-to-end tests.
- Run `pytest -q` with zero failures.
- Run `ruff check .` with zero errors.
- Run `mypy --strict .` with zero errors.
- Ensure no required file contains a stub or masked command failure.

## Machine-Readable Contract

```noctifab-contract
{"story_id": "US-004","public_contracts":[{"id":"schedule-status-http","interface":"HTTP GET /api/v1/boards/{board_id}/schedule-status","allowed_executables":["python3.12 src/manage.py runserver 127.0.0.1:8000","pytest -q"],"exit_codes":[0,1],"stdout_contains":["application/json","status"],"stderr_prefixes":["CommandError:"]},{"id":"management-http","interface":"HTTP JSON REST /api/v1/boards, /api/v1/boards/{board_id}/lists, /api/v1/boards/{board_id}/cards","allowed_executables":["python3.12 src/manage.py runserver 127.0.0.1:8000","pytest -q"],"exit_codes":[0,1],"stdout_contains":["application/json"],"stderr_prefixes":["CommandError:"]}]}
```
