# US-003: Time Tracking and Lead Cycle Analytics

## Story

As a delivery manager, I want reliable time and flow metrics, so I can compare effort, workload, lead time, and cycle time.

## Scope

Implement Plus for Trello comment parsing and workload aggregation. Implement lead-time and cycle-time statistics. Expose both calculations through authenticated Django REST endpoints.

Use Python 3.12+ and Django 5.x. Keep domain code independent of Django. Preserve the legacy code through characterization tests from US-001.

## Depends On

- US-001

## Change Type

new

## Observable Entry Point

Use the repository entry point at `src/manage.py`.

Run the application with:

`python src/manage.py runserver 127.0.0.1:8000 --noreload`

Run unit and integration tests with:

`pytest -q`

Run static checks with:

`ruff check .`

`mypy --strict .`

The HTTP protocol uses HTTP/1.1 or HTTP/2 over TCP. The API uses JSON UTF-8 responses. Clients must send `Accept: application/json`. Authenticated requests must send the authentication mechanism established by US-001 and the current API configuration.

## Public HTTP Contracts

### Time tracking

Send:

`GET /api/v1/boards/{board_id}/time-tracking`

Require an authenticated user who can view the board.

Return status `200` with this JSON object:

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

Return members in ascending `member_id` order. Return totals with two decimal places. Return an empty array when no parsed comment has a member. Do not omit required keys.

### Lead and cycle statistics

Send:

`GET /api/v1/boards/{board_id}/lead-cycle-times`

Require an authenticated user who can view the board.

Return status `200` with this JSON object:

```json
{
  "board_id": "b-101",
  "avg_lead_time_days": 4.50,
  "median_lead_time_days": 3.80,
  "min_lead_time_days": 1.25,
  "max_lead_time_days": 8.00,
  "avg_cycle_time_days": 2.10,
  "median_cycle_time_days": 1.90,
  "min_cycle_time_days": 0.50,
  "max_cycle_time_days": 5.00
}
```

Return all statistic keys. Return `0.00` for each statistic when no completed card has valid timing data.

### Error envelope

Return this JSON object for API errors:

```json
{
  "error": {
    "code": "BOARD_NOT_FOUND",
    "message": "Board was not found."
  }
}
```

Use status `400` for invalid path input or invalid source data. Use status `401` for missing authentication. Use status `403` for insufficient board access. Use status `404` for an unknown board. Use status `500` only for an unexpected server failure. Do not expose stack traces or secrets.

## Domain Rules

### Plus for Trello parser

Create `PlusForTrelloParser` as a pure Python service.

Parse a comment when it contains one standalone token in this form: `(spent/estimated)`.

Accept decimal values with an optional leading plus sign and up to four fractional digits. Accept `0` and values such as `2.5`, `2.50`, and `+2.5000`. Reject negative values, empty values, commas, exponents, and additional slash components.

Use a full-token match after trimming surrounding whitespace. Ignore ordinary prose and malformed tokens. Treat `spent > estimated` as valid because actual effort can exceed the estimate.

Represent parsed values with `Decimal`. Convert values to non-negative hours. Round only aggregate output with `Decimal.quantize(Decimal("0.01"), ROUND_HALF_UP)`.

Attach the comment author as `member_id` when the source comment has an author. Preserve the source member name for the response. A comment without an author contributes to card, list, and board totals, but it does not contribute to `member_workload`.

If one comment contains several valid tokens, parse each token in source order. If a comment contains no valid token, contribute nothing. Never raise an exception for ordinary malformed comment text.

### Workload aggregation

Create `TimeTracker` as a pure Python service.

Aggregate parsed spent and estimated hours for every card, list, board, and member. The public endpoint returns board totals and member totals.

Count each parsed token once. Preserve decimal precision during accumulation. Round only the final values returned by the domain result and the API serializer.

Sort member records by `member_id`. Use the source member name for each member record. Reject conflicting names for one member within one calculation with a typed domain validation error.

### Lead time

Create `LeadCycleCalculator` as a pure Python service.

Measure lead time from card creation to the first transition into a list marked `done`. Use elapsed seconds divided by `86400` for day values.

Include only cards with a creation timestamp, a valid first done transition, and a non-negative duration. Use the first qualifying done transition. Exclude incomplete cards from aggregate statistics.

### Cycle time

Mark each list as `backlog`, `active`, or `done` in the pure input model. Sum time spent in active lists only. Exclude backlog and done intervals.

Use ordered transition timestamps. For each interval, use the current list and the next transition timestamp. For a completed card, close the final active interval at the first done transition. Ignore intervals with missing or invalid timestamps.

Include a card only when its cycle duration is valid and non-negative. A valid zero-duration cycle is `0.00` days.

### Statistics

Calculate average, median, minimum, and maximum for lead and cycle durations.

Use arithmetic mean. Use the standard median: return the middle value for an odd count and the mean of the two middle values for an even count. Sort values before calculating median. Round public values to two decimal places with `ROUND_HALF_UP`.

Use timezone-aware UTC timestamps internally. Reject naive timestamps at domain boundaries with a typed validation error. Do not read the system clock during a calculation.

## Input Models

Define immutable, typed domain models for:

- `BoardSnapshot` with `board_id`, cards, lists, and members.
- `CardSnapshot` with `card_id`, `title`, `created_at`, comments, and transitions.
- `CommentSnapshot` with `body`, `author_id`, and `author_name`.
- `ListSnapshot` with `list_id`, `name`, and workflow category.
- `TransitionSnapshot` with `occurred_at` and `list_id`.
- `MemberWorkload` and `LeadCycleStatistics` result values.

Use protocols for the data source. Define `TrelloClient` in `src/djanban/domain/ports.py`. Inject it into API handlers or application services through constructors. Never call the network from domain services or tests.

## Required Repository Paths

Create or update these exact paths:

- `src/djanban/domain/__init__.py`
- `src/djanban/domain/errors.py`
- `src/djanban/domain/models.py`
- `src/djanban/domain/ports.py`
- `src/djanban/domain/plus_for_trello_parser.py`
- `src/djanban/domain/time_tracker.py`
- `src/djanban/domain/lead_cycle_calculator.py`
- `src/djanban/api/__init__.py`
- `src/djanban/api/auth.py`
- `src/djanban/api/serializers.py`
- `src/djanban/api/views/analytics.py`
- `src/djanban/api/urls.py`
- `src/djanban/urls.py`
- `tests/domain/test_plus_for_trello_parser.py`
- `tests/domain/test_time_tracker.py`
- `tests/domain/test_lead_cycle_calculator.py`
- `tests/api/test_time_tracking_endpoint.py`
- `tests/api/test_lead_cycle_endpoint.py`
- `tests/api/test_analytics_authentication.py`
- `tests/support/fakes.py`
- `tests/support/clock.py`

Keep handlers, serializers, and domain services in separate modules. Internal modules must import direct modules, not package facades or index modules. Do not create a monolithic analytics module.

## Testing Requirements

Use Chicago-school tests. Test observable behavior through public methods and HTTP responses. Do not test private implementation details.

Create in-memory fakes in `tests/support/fakes.py`. Implement an in-memory `TrelloClient` fake. Do not use network calls, real Trello credentials, or external services.

Create a deterministic mock clock in `tests/support/clock.py`. Inject it into any application service that needs the current time. Every time test must use fixed UTC timestamps. Do not use `datetime.now()`, `datetime.utcnow()`, sleep calls, or time-based polling.

Use Django test clients and in-memory SQLite for integration tests. Test authentication, authorization, status codes, JSON keys, numeric precision, and error envelopes.

Run black-box E2E tests against a real local server. Poll the socket until it accepts connections. Set a bounded timeout. Do not use a static sleep delay. Cover every public endpoint and every scenario in the matrix.

## Scenario and Edge Case Matrix

| ID | Scenario | Expected result |
|---|---|---|
| TT-01 | Parse `(2.5/4.0)` | Return spent `2.50` and estimated `4.00`. |
| TT-02 | Parse `(0/0)` | Return two zero values. |
| TT-03 | Parse `(+2.5000/+4.0000)` | Return valid decimal values. |
| TT-04 | Parse malformed text | Ignore the text without an exception. |
| TT-05 | Parse `(-1/2)` | Ignore the token. |
| TT-06 | Parse `(1,5/2)` | Ignore the token. |
| TT-07 | Parse `(1e2/2)` | Ignore the token. |
| TT-08 | Parse several valid tokens | Aggregate each token once in source order. |
| TT-09 | Parse a comment without an author | Add board totals and no member record. |
| TT-10 | Use conflicting names for one member | Return a typed validation error and HTTP `400`. |
| TT-11 | Aggregate no comments | Return zero totals and an empty member array. |
| TT-12 | Aggregate fractional hours | Round final values to two decimal places. |
| LC-01 | Card reaches done once | Use the first done transition for lead time. |
| LC-02 | Card does not reach done | Exclude the card from lead statistics. |
| LC-03 | Card spends time in backlog | Exclude backlog time from cycle time. |
| LC-04 | Card spends time in active lists | Sum active intervals only. |
| LC-05 | Card reaches done after active work | Close the active interval at done time. |
| LC-06 | Card has zero active duration | Include `0.00` cycle time. |
| LC-07 | Card has a negative interval | Exclude the invalid metric. |
| LC-08 | Card has a naive timestamp | Return a typed validation error. |
| LC-09 | One statistic has an even sample count | Use the mean of the two middle values. |
| LC-10 | No valid completed cards exist | Return zero for every statistic. |
| API-01 | Authenticated board request | Return status `200` and the exact response envelope. |
| API-02 | Missing authentication | Return status `401` and the error envelope. |
| API-03 | User lacks board access | Return status `403` and the error envelope. |
| API-04 | Unknown board | Return status `404` and the error envelope. |
| API-05 | Invalid board identifier | Return status `400` without a traceback. |
| API-06 | Unexpected source failure | Return status `500` without internal details. |
| API-07 | Unsupported method | Return status `405` with a JSON error response. |
| API-08 | Non-JSON accept header | Return the configured API error response, not HTML. |

## Anti-Stub and Negative Constraints

Do not add `pass`, ellipsis expressions, `NotImplementedError`, placeholder return values, fake success responses, or disabled assertions.

Do not mask errors with `|| true`, broad exception swallowing, or skipped tests without a documented environment reason. Do not use network access in unit or integration tests. Do not use Django ORM objects inside domain calculators. Do not use floating-point arithmetic for hour accumulation or statistic calculation.

Do not add AngularJS code. Do not add a second API version. Do not change the US-002 contracts. Do not remove US-001 characterization tests.

## Standard Output and Exit Codes

The application server must write startup logs to stderr or the configured Django logger. It must not write analytics JSON to stdout during HTTP operation.

`pytest -q` must exit `0` only when every test passes. It must exit non-zero on any failure, error, collection error, or missing test.

`ruff check .` must exit `0` with no diagnostics. `mypy --strict .` must exit `0` with no diagnostics.

Test runners must write failure diagnostics to stderr. Diagnostics for this story must begin with `US-003 ERROR:`. Do not suppress command output.

## Definition of Done

- Implement all required domain models, ports, parsers, calculators, serializers, views, and routes.
- Serve both endpoints under `/api/v1/boards/{board_id}/...`.
- Enforce authentication and board authorization.
- Return the exact JSON keys and error envelope defined here.
- Apply deterministic UTC time handling and `ROUND_HALF_UP` output rounding.
- Use in-memory fakes for domain and integration tests.
- Cover every scenario in the matrix.
- Pass `pytest -q` with a 100 percent pass rate.
- Pass black-box E2E tests with socket readiness polling.
- Pass `ruff check .` with zero diagnostics.
- Pass `mypy --strict .` with zero diagnostics.
- Leave no stubs, placeholders, masked errors, or skipped required scenarios.

```noctifab-contract
{"story_id": "US-003","public_contracts":[{"id":"time-tracking-http","interface":"GET /api/v1/boards/{board_id}/time-tracking","allowed_executables":["python src/manage.py runserver 127.0.0.1:8000 --noreload","pytest -q"],"exit_codes":[0,1,2],"stdout_contains":["pytest"],"stderr_prefixes":["US-003 ERROR:"]},{"id":"lead-cycle-http","interface":"GET /api/v1/boards/{board_id}/lead-cycle-times","allowed_executables":["python src/manage.py runserver 127.0.0.1:8000 --noreload","pytest -q"],"exit_codes":[0,1,2],"stdout_contains":["pytest"],"stderr_prefixes":["US-003 ERROR:"]}]}
```