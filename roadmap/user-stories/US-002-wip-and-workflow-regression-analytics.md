# US-002: WIP and Workflow Regression Analytics

## Story

As an authenticated board member, I want WIP and regression metrics, so I can find workflow control problems.

## Metadata

- Story ID: US-002
- Domain capability: WIP Calculator and Regression Tracker
- Depends on: US-001
- Complexity: 26 CU
- Change type: new
- Runtime: Python 3.12 or later and Django 5.x

## Scope

Implement typed domain models for board lists, cards, transitions, and WIP limits.
Implement pure WIP and regression calculators without Django imports.
Expose authenticated read-only endpoints under `/api/v1/`.
Use the existing legacy board data through an injected `TrelloClient` protocol.
Preserve the characterization safety rails from US-001.

Do not implement time tracking, lead time, cycle time, schedule status, or management mutations.
Do not add an AngularJS feature.

## Observable Entry Points

Use these commands from the repository root:

- `python -m pytest tests/unit/domain/test_wip.py tests/unit/domain/test_regressions.py -q`
- `python -m pytest tests/integration/api/test_analytics_endpoints.py -q`
- `python -m pytest tests/e2e/test_analytics_http.py -q`
- `python manage.py check`
- `python manage.py runserver 127.0.0.1:8000 --noreload`

The Django entrypoint is `src/manage.py` when the repository uses the legacy `src` layout.
The modern project entrypoint is `manage.py` when US-001 creates a root entrypoint.
Select one layout and use it consistently in all project configuration.

The HTTP protocol is HTTP/1.1 over TCP.
The API uses UTF-8 JSON and the `application/json` media type.
The endpoint accepts `GET` only.
The endpoint rejects request bodies and unsupported methods.

Authentication must run before board lookup.
An unauthenticated request must return HTTP `401` with this exact JSON body:
`{"detail":"Authentication credentials were not provided."}`
An authenticated user without board access must return HTTP `403` with this exact JSON body:
`{"detail":"You do not have permission to access this board."}`

## WIP Domain Contract

Create `WIPCalculator` as a pure callable service.
Accept a typed board identifier and an iterable of typed list snapshots.
Count cards from the supplied snapshot, not from HTTP request data.

Each list snapshot contains `list_id`, `list_name`, `card_count`, `min_wip`, and `max_wip`.
Identifiers and names are non-empty strings.
`card_count` is an integer greater than or equal to zero.
Each limit is either null or an integer greater than or equal to zero.
When both limits exist, `min_wip` must not exceed `max_wip`.
Reject invalid values with a domain validation error.

Use inclusive limits.
Return `UNDER_WIP` when the count is below `min_wip`.
Return `OVER_WIP` when the count is above `max_wip`.
Return `WITHIN_WIP` when all supplied limits contain the count.
Return `NO_LIMIT` when both limits are absent.
A count equal to either limit is within the limit.

The endpoint response must contain exactly these top-level keys:
`board_id` and `lists`.
Each list object must contain exactly these keys:
`list_id`, `list_name`, `card_count`, `max_wip`, and `status`.
Use JSON null for an absent `max_wip`.
Do not expose `min_wip` in this endpoint response.
Preserve workflow list order from the data source.

For board `b-101`, a list named `In Progress` with five cards and maximum WIP three must produce this exact response shape:
`{"board_id":"b-101","lists":[{"list_id":"l-in-progress","list_name":"In Progress","card_count":5,"max_wip":3,"status":"OVER_WIP"}]}`
Do not add envelope keys, debug fields, timestamps, or framework metadata.

## Regression Domain Contract

Create `RegressionTracker` as a pure callable service.
Accept typed cards, ordered lists, and card transition histories.
Order lists by a unique positive integer `workflow_order`.
Reject duplicate list identifiers, duplicate workflow orders, or unknown list identifiers.

Record one regression when a transition moves from a higher workflow order to a lower workflow order.
Do not record a transition between equal orders as a regression.
Do not record a forward transition as a regression.
Count repeated regressions separately.
Ignore no transition silently; reject malformed transitions.

Return total regressions, total transitions, regression rate, and regressed card details.
Calculate `regression_rate` as `total_regressions / total_transitions`.
Return `0.0` when there are no transitions.
Round the rate to two decimal places using decimal half-up rounding.
Return cards in stable card identifier order.
Return the last regression in chronological input order.

The endpoint response must contain exactly these top-level keys:
`board_id`, `total_regressions`, `regression_rate`, and `regressed_cards`.
Each regressed card object must contain exactly these keys:
`card_id`, `title`, `regression_count`, `last_regression_from`, and `last_regression_to`.
Do not include cards with zero regressions.

For four regressions across thirty-three transitions, return `regression_rate` as `0.12`.
For no transitions, return `total_regressions` as `0` and `regression_rate` as `0.0`.

## HTTP Contracts

Implement `GET /api/v1/boards/{board_id}/wip-status`.
Return HTTP `200` with the exact WIP JSON contract on success.
Implement `GET /api/v1/boards/{board_id}/regressions`.
Return HTTP `200` with the exact regression JSON contract on success.

Return HTTP `400` for an invalid board identifier or invalid domain data.
Return this exact JSON error body for invalid input:
`{"detail":"Invalid analytics input."}`
Return HTTP `404` when the authenticated user can access the service but the board does not exist.
Return this exact JSON error body for a missing board:
`{"detail":"Board not found."}`
Return HTTP `405` for unsupported methods.
Return HTTP `500` only for an unexpected server defect.
Never expose a traceback, secret, database detail, or internal class name.

Set `Content-Type: application/json; charset=utf-8` on every JSON response.
Use compact JSON without insignificant whitespace in black-box assertions.
Serialize all identifiers and names as JSON strings.
Serialize counts as JSON integers.
Serialize rates as JSON numbers, not strings.

## Typed and Modular Design

Create these exact repository-relative files:

- `src/djanban/domain/__init__.py`
- `src/djanban/domain/models.py`
- `src/djanban/domain/wip.py`
- `src/djanban/domain/regressions.py`
- `src/djanban/domain/ports.py`
- `src/djanban/api/__init__.py`
- `src/djanban/api/analytics_views.py`
- `src/djanban/api/analytics_serializers.py`
- `src/djanban/api/urls.py`
- `src/djanban/api/errors.py`
- `src/djanban/urls.py`
- `tests/unit/domain/test_wip.py`
- `tests/unit/domain/test_regressions.py`
- `tests/unit/domain/test_models.py`
- `tests/integration/api/test_analytics_endpoints.py`
- `tests/e2e/test_analytics_http.py`
- `tests/doubles/in_memory_trello_client.py`

Define `TrelloClient` in `src/djanban/domain/ports.py` as a typed protocol.
Inject it into the application service or view factory constructor.
Do not import Django, ORM models, HTTP objects, or serializers into domain modules.
Do not import parent package facades or index modules from internal handlers.
Import concrete modules directly to prevent circular imports.
Keep HTTP mapping, authentication, and domain calculation separate.

## Test Invariants

Use Chicago-school tests with observable behavior and state verification.
Author and use `InMemoryTrelloClient` for unit, integration, and end-to-end setup.
Do not call Trello, a network service, or a production database in unit tests.
Use pytest-django with an in-memory SQLite database for integration tests.

Cover these WIP scenarios:

| Scenario | Expected result |
|---|---|
| Count equals minimum | `WITHIN_WIP` |
| Count equals maximum | `WITHIN_WIP` |
| Count below minimum | `UNDER_WIP` |
| Count above maximum | `OVER_WIP` |
| Both limits absent | `NO_LIMIT` |
| Only minimum present | Apply only the minimum |
| Only maximum present | Apply only the maximum |
| Zero cards | Valid count |
| Negative count | Domain validation error |
| Minimum above maximum | Domain validation error |
| Empty identifier or name | Domain validation error |
| Multiple lists | Preserve source order |

Cover these regression scenarios:

| Scenario | Expected result |
|---|---|
| Higher order to lower order | Count one regression |
| Lower order to higher order | Count no regression |
| Equal workflow order | Count no regression |
| Repeated backward moves | Count each move |
| No transitions | Rate `0.0` |
| Four of thirty-three transitions regress | Rate `0.12` |
| Unknown list | Validation error |
| Duplicate list order | Validation error |
| Empty card title | Validation error |
| Empty transition history | Valid zero result |
| Unsorted input histories | Use supplied chronological order |

Cover these HTTP scenarios:

| Request | Expected status |
|---|---:|
| Authenticated valid WIP request | 200 |
| Authenticated valid regression request | 200 |
| Missing authentication | 401 |
| Forbidden board | 403 |
| Missing board | 404 |
| Malformed board identifier | 400 |
| Invalid domain snapshot | 400 |
| Unsupported method | 405 |
| Unexpected exception | 500 without internals |

Use exact JSON equality in integration assertions.
Assert status, content type, response keys, value types, and absence of extra keys.
Assert that unauthenticated requests do not invoke the client.
Assert that forbidden requests do not expose board data.

No feature in this story uses time, TTL, or expiration.
If an implementation adds time behavior, inject a deterministic mock clock and test every boundary.
Do not use wall-clock assertions.

## Black-Box End-to-End Verification

Start the Django server with `python manage.py runserver 127.0.0.1:8000 --noreload`.
Poll the TCP socket until it accepts a connection.
Stop polling after a bounded timeout and fail the test if readiness is absent.
Do not use static sleep delays.
Exercise every scenario in the HTTP matrix through a real socket.
Send an authentication request before protected requests.
Assert the complete status, headers, and JSON body.
Stop the server in test teardown.

## Anti-Stub and Negative Constraints

Implement every listed module and test.
Do not use `pass`, ellipsis expressions, `NotImplementedError`, placeholder returns, or skipped required tests.
Do not mask failures with `|| true`, broad exception swallowing, or unconditional success exits.
Do not use network calls in unit or integration tests.
Do not add AngularJS dependencies.
Do not place calculation logic in Django views, serializers, or ORM models.
Do not use floating-point arithmetic for regression-rate calculation.
Do not return HTML, plain text, or framework debug pages from API errors.

## Standard I/O and Exit Contracts

Commands must write normal progress to stdout and diagnostics to stderr.
A successful test command must exit `0` and stdout must contain `passed`.
A failed test command must exit non-zero and stderr must begin with `ERROR:` or stdout must contain `failed`.
`python manage.py check` must exit `0` and stdout must contain `System check identified no issues`.
A failed system check must exit non-zero and stderr must begin with `ERROR:`.
The HTTP server must write startup and error diagnostics to stderr.
No command may suppress an error or convert a failure to exit `0`.

## Definition of Done

- Implement all required files and contracts.
- Pass all unit tests with zero failures.
- Pass all integration tests with zero failures.
- Pass all black-box end-to-end scenarios with zero failures.
- Run `ruff check .` with zero errors.
- Run `mypy --strict .` with zero errors.
- Run `python manage.py check` successfully.
- Verify authentication before board access.
- Verify exact JSON keys, value types, precision, and error bodies.
- Verify no prohibited stub or shell pattern exists.
- Preserve US-001 characterization tests and pass them.

## Machine-Readable Contract

```noctifab-contract
{
  "story_id": "US-002",
  "public_contracts": [
    {
      "id": "wip-status-http",
      "interface": "GET /api/v1/boards/{board_id}/wip-status",
      "allowed_executables": ["python", "python3", "curl", "pytest"],
      "exit_codes": [0, 1, 2],
      "stdout_contains": ["board_id", "lists", "status"],
      "stderr_prefixes": ["ERROR:"]
    },
    {
      "id": "regressions-http",
      "interface": "GET /api/v1/boards/{board_id}/regressions",
      "allowed_executables": ["python", "python3", "curl", "pytest"],
      "exit_codes": [0, 1, 2],
      "stdout_contains": ["board_id", "total_regressions", "regression_rate"],
      "stderr_prefixes": ["ERROR:"]
    }
  ]
}
```
