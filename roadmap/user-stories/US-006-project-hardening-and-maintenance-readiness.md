# US-006: Project Hardening, Maintenance Readiness and Code Quality

## Story

As a maintainer, I want a repeatable quality gate for the modernized project, so I can release changes with clear evidence.

## Scope

Apply formatting and import hygiene across the supported Python source tree. Run static analysis and the complete test suite. Verify HTTP behavior through a running Django process. Build the package and run executable sanity checks. Document the commands, interfaces, limits, and failure rules.

Keep legacy behavior covered by characterization tests. Keep domain logic independent from Django. Keep all tests offline. Do not restore AngularJS as an active application dependency.

## Dependencies

- Depends on: US-001, US-002, US-003, US-004, US-005
- Change type: new
- Complexity: 28 CU

## Required repository paths

Create or update these exact paths:

- `pyproject.toml`
- `README.md`
- `CHANGELOG.md`
- `docs/operations/quality-gates.md`
- `docs/api/v1.md`
- `scripts/quality_gate.py`
- `scripts/black_box_http.py`
- `scripts/package_sanity.py`
- `src/manage.py`
- `src/djanban/settings.py`
- `src/djanban/urls.py`
- `src/djanban/apps/api/urls.py`
- `src/djanban/apps/api/views/boards.py`
- `src/djanban/apps/api/views/cards.py`
- `src/djanban/apps/api/views/lists.py`
- `src/djanban/apps/api/serializers.py`
- `src/djanban/domain/wip.py`
- `src/djanban/domain/regression.py`
- `src/djanban/domain/time_tracking.py`
- `src/djanban/domain/lead_cycle.py`
- `src/djanban/domain/schedule.py`
- `tests/conftest.py`
- `tests/unit/test_wip.py`
- `tests/unit/test_regression.py`
- `tests/unit/test_time_tracking.py`
- `tests/unit/test_lead_cycle.py`
- `tests/unit/test_schedule.py`
- `tests/integration/test_api_contracts.py`
- `tests/integration/test_management_api.py`
- `tests/e2e/test_black_box_http.py`
- `tests/characterization/test_legacy_boards.py`
- `tests/characterization/test_legacy_cards.py`
- `tests/characterization/test_legacy_lists.py`
- `tests/characterization/test_legacy_authentication.py`
- `tests/characterization/test_legacy_api.py`
- `tests/test_quality_gate.py`
- `tests/test_package_sanity.py`

Internal modules must import direct modules. They must not import parent package facades or index modules. Keep each handler, serializer, calculator, command, and test in its named file. Do not create a monolith.

## Observable commands

Run commands from the repository root. Use Python 3.12 or newer.

- `python scripts/quality_gate.py`
- `python scripts/black_box_http.py --host 127.0.0.1 --port 8765 --startup-timeout 10`
- `python scripts/package_sanity.py`
- `python -m ruff format --check .`
- `python -m ruff check .`
- `python -m mypy --strict src`
- `python -m pytest -q`
- `python src/manage.py check --deploy`
- `python -m build --wheel --sdist`
- `python -m pip install --no-deps --target .quality-install dist/*.whl`

The quality gate must execute formatting checks, Ruff, strict mypy, Django checks, pytest, black-box HTTP checks, package creation, and package sanity checks. It must stop after the first failed command. It must return the failed command exit status, or `1` when the status cannot be read.

Do not use `|| true`, ignored errors, empty handlers, `pass`, ellipsis bodies, or `NotImplementedError`. Do not hide output. Do not skip tests through command flags. Do not add network access to tests.

## Thin command wrappers

Keep `scripts/quality_gate.py`, `scripts/black_box_http.py`, and `scripts/package_sanity.py` below 15 lines of executable wrapper code. Each wrapper must call a function in a direct implementation module immediately. The wrapper must not contain business logic. Use explicit return values and `SystemExit`.

If a package command requires a module, place it at `src/djanban/maintenance/quality_gate.py`, `src/djanban/maintenance/black_box_http.py`, or `src/djanban/maintenance/package_sanity.py`. Add those paths only when used. Keep imports direct and acyclic.

## Standard input, output, and exit rules

Commands accept no standard input. They must not prompt. UTF-8 is the required encoding.

On success, `scripts/quality_gate.py` must write these lines to standard output in this order:

- `QUALITY_GATE START`
- `QUALITY_GATE FORMAT PASS`
- `QUALITY_GATE RUFF PASS`
- `QUALITY_GATE MYPY PASS`
- `QUALITY_GATE DJANGO PASS`
- `QUALITY_GATE PYTEST PASS`
- `QUALITY_GATE HTTP PASS`
- `QUALITY_GATE PACKAGE PASS`
- `QUALITY_GATE COMPLETE`

On success, `scripts/black_box_http.py` must write `BLACK_BOX_HTTP PASS`.

On success, `scripts/package_sanity.py` must write `PACKAGE_SANITY PASS`.

Successful commands write no standard error and return exit status `0`. A command error must write `ERROR: <command>: <reason>` to standard error and return a non-zero status. An invalid argument must write `ERROR: invalid argument: <name>` and return `2`. A startup timeout must write `ERROR: server readiness timeout` and return `3`.

Do not compare output by substring when an exact line is required. Preserve command order and exit status.

## HTTP black-box protocol

Start Django with `python src/manage.py runserver 127.0.0.1:8765 --noreload`. Poll the socket until it accepts a connection. Poll at 100 millisecond intervals. Stop after 10 seconds. Do not use a static sleep as readiness control.

Send HTTP/1.1 requests with `Host`, `Accept: application/json`, and a `Connection: close` header. Use authenticated test credentials created by the test fixture. Send a CSRF token for every state-changing request. Use JSON UTF-8 request bodies.

Verify these read contracts:

- `GET /api/v1/boards/{board_id}/wip-status`
- `GET /api/v1/boards/{board_id}/regressions`
- `GET /api/v1/boards/{board_id}/time-tracking`
- `GET /api/v1/boards/{board_id}/lead-cycle-times`
- `GET /api/v1/boards/{board_id}/schedule-status`

Verify management contracts for board, card, and list routes from US-004. Verify authentication, authorization, CSRF rejection, validation errors, not-found errors, and malformed JSON.

Every successful JSON response must contain `Content-Type: application/json`. Every error response must contain a JSON object with `error` and `message` string fields. Do not return HTML for API errors.

Use these status rules:

- Return `200` for valid read requests.
- Return `201` for valid resource creation.
- Return `204` for valid deletion with no response body.
- Return `400` for malformed JSON or invalid fields.
- Return `401` when authentication is missing.
- Return `403` when authentication lacks permission or CSRF protection rejects a request.
- Return `404` when the board or resource does not exist.
- Return `405` for an unsupported HTTP method.

Use the exact domain response keys from SPEC.md. Use JSON numbers, not numeric strings. Round calculated hours and percentages to two decimal places. Preserve `0.00` for zero values. Reject negative hours, reversed time intervals, missing identifiers, duplicate list order values, and thresholds where `min_wip` exceeds `max_wip`.

## Quality and packaging rules

Configure `pyproject.toml` for Python 3.12 or newer, Django 5.x, pytest-django, Ruff, mypy, and the supported package metadata. Pin compatible lower bounds. Set Ruff and mypy to inspect the supported source and test paths. Exclude generated build directories and `.quality-install` from analysis.

Format Python files with Ruff. Remove unused imports, wildcard imports, unreachable branches, and obsolete compatibility imports. Keep public interfaces typed. Use strict mypy without broad type ignores. Each ignore must name a specific error code and include a local reason.

Build both wheel and source distributions. Install the wheel into `.quality-install` without network access. Run `python -c "import djanban"` with the installed target on `PYTHONPATH`. Run `python src/manage.py check` with the installed package and a temporary SQLite database. Remove temporary artifacts after the check.

Do not include AngularJS files as active runtime dependencies. Do not add network calls to package checks or tests. Do not modify domain calculations to satisfy a test without preserving the specified invariant.

## Test design

Use Chicago-school tests. Assert observable state and output. Do not assert private implementation calls.

Create in-memory test doubles for Trello data, the clock, repositories, HTTP transport, and process readiness. Unit and integration tests must use these doubles. Unit tests must not use Django ORM or network sockets. Integration tests must use in-memory SQLite and `pytest-django`. Black-box tests may use a local process only.

Use a deterministic mock clock for every timestamp, duration, expiration, and readiness deadline. Never use the wall clock in a domain or test assertion. Use fixed UUIDs, identifiers, ordering, and JSON fixtures.

## Scenario and edge-case matrix

Cover every row with unit, integration, or black-box tests as appropriate:

| Area | Scenario | Expected result |
|---|---|---|
| Formatting | A file has an import-order error | Ruff fails and reports the file; the gate returns non-zero |
| Typing | A value violates a declared type | strict mypy fails; the gate returns non-zero |
| Tests | One test fails | pytest fails; later gate steps do not run |
| WIP | Count equals minimum or maximum | Status is within limits |
| WIP | Count is below minimum | Status is `UNDER_WIP` |
| WIP | Count is above maximum | Status is `OVER_WIP` |
| WIP | No threshold exists | The contract uses the defined null threshold behavior |
| WIP | Minimum exceeds maximum | Return `400` with a validation error |
| Regression | A card moves to an earlier list | Count one regression |
| Regression | A card moves to the same or later list | Count zero regressions |
| Regression | No transitions exist | Return rate `0.00` |
| Time | Comment contains `(2.5/4.0)` | Parse spent `2.50` and estimated `4.00` |
| Time | Comment has malformed, negative, or multiple values | Reject malformed values and report a validation error without partial totals |
| Time | No comments exist | Return zero totals |
| Lead/cycle | Card has no Done entry | Exclude it from completed duration statistics |
| Lead/cycle | Active interval is zero | Include `0.00` when the interval is valid |
| Lead/cycle | Events are unordered | Sort by deterministic event time and identifier |
| Schedule | Total estimate is zero | Return a documented validation error; never divide by zero |
| Schedule | Completion is exactly five points behind time spent | Status is `ON_TIME` |
| Schedule | Completion is more than five points behind | Status is `BEHIND_SCHEDULE` |
| HTTP | Missing credentials | Return `401` and the JSON error envelope |
| HTTP | Wrong board owner | Return `403` and the JSON error envelope |
| HTTP | Missing CSRF token on mutation | Return `403` and the JSON error envelope |
| HTTP | Unknown board | Return `404` and the JSON error envelope |
| HTTP | Invalid JSON | Return `400` and the JSON error envelope |
| HTTP | Unsupported method | Return `405` and the JSON error envelope |
| HTTP | Read request succeeds | Return the exact documented JSON keys and numeric formats |
| Process | Port is unavailable | Return a non-zero status and the standard error prefix |
| Process | Server never becomes ready | Return status `3` and `ERROR: server readiness timeout` |
| Package | Wheel imports successfully | Print `PACKAGE_SANITY PASS` and return `0` |
| Package | Required metadata is missing | Return non-zero and print the standard error prefix |

## Acceptance criteria

1. Run `python scripts/quality_gate.py` in a clean environment. Confirm every required pass line. Confirm exit status `0`.
2. Run `python -m ruff check .`. Confirm zero errors and zero warnings.
3. Run `python -m mypy --strict src`. Confirm zero errors.
4. Run `python -m pytest -q`. Confirm a 100 percent pass rate and zero failures.
5. Run the black-box HTTP suite. Confirm socket polling, all listed routes, all error statuses, and exact JSON envelopes.
6. Build a wheel and source distribution. Install the wheel without network access. Confirm the package sanity result.
7. Confirm no forbidden stub, placeholder, ignored shell error, or active AngularJS runtime dependency exists in supported source.
8. Confirm the operations and API documents describe all commands, routes, status codes, output lines, number rules, and failure rules.
9. Confirm all tests use deterministic clocks and in-memory doubles where the test type requires them.
10. Confirm legacy characterization tests still pass without unexplained behavior changes.

## Definition of Done

- All acceptance criteria pass.
- Unit, integration, characterization, and black-box E2E suites pass at 100 percent.
- Ruff format check, Ruff lint, strict mypy, Django deploy checks, packaging, and package sanity checks pass.
- No command masks an error.
- No required implementation contains a stub or placeholder.
- Documentation is complete and matches the executable behavior.
- The change is ready for maintenance and release review.

```noctifab-contract
{"story_id": "US-006","public_contracts":[{"id":"quality-gate-cli","interface":"process stdin/stdout/stderr","allowed_executables":["python scripts/quality_gate.py","python -m ruff format --check .","python -m ruff check .","python -m mypy --strict src","python -m pytest -q","python src/manage.py check --deploy","python -m build --wheel --sdist"],"exit_codes":{"success":0,"invalid_argument":2,"readiness_timeout":3,"failure":"non-zero"},"stdout_contains":["QUALITY_GATE START","QUALITY_GATE COMPLETE"],"stderr_prefixes":["ERROR: "]},{"id":"black-box-http-api","interface":"HTTP/1.1 JSON over TCP","allowed_executables":["python scripts/black_box_http.py --host 127.0.0.1 --port 8765 --startup-timeout 10","python src/manage.py runserver 127.0.0.1:8765 --noreload"],"exit_codes":{"success":0,"invalid_argument":2,"readiness_timeout":3,"failure":"non-zero"},"stdout_contains":["BLACK_BOX_HTTP PASS"],"stderr_prefixes":["ERROR: "]},{"id":"package-sanity","interface":"local Python import and Django check","allowed_executables":["python scripts/package_sanity.py","python -m pip install --no-deps --target .quality-install dist/*.whl"],"exit_codes":{"success":0,"failure":"non-zero"},"stdout_contains":["PACKAGE_SANITY PASS"],"stderr_prefixes":["ERROR: "]}]}
```