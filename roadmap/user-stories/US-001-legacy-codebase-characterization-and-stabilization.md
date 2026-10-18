# US-001: Legacy Codebase Characterization and Stabilization

## Story

As a maintainer, create a tested Django 5 entrypoint and record stable legacy behavior.

Use Python 3.12 or later. Use Django 5.x. Preserve the legacy source tree under `src/`.

Do not implement WIP, regression, time, lead time, cycle time, or schedule analytics.

## Scope

Create a thin Django entrypoint. Add the `/healthz` endpoint. Add characterization tests for boards, cards, lists, authentication, and existing API routes.

Keep domain calculations outside Django handlers. Use dependency injection for external services. Use offline test doubles in all tests.

Do not add AngularJS dependencies. Do not add a new frontend.

## Dependencies

- Depends on: `[]`
- Change type: `new`
- Complexity: `30 CU`

## Required Files

Create or update these focused files:

- `manage.py`
- `pyproject.toml`
- `djanban/__init__.py`
- `djanban/settings.py`
- `djanban/urls.py`
- `djanban/wsgi.py`
- `djanban/health.py`
- `djanban/domain/__init__.py`
- `djanban/api/__init__.py`
- `tests/conftest.py`
- `tests/unit/test_health.py`
- `tests/integration/test_health_endpoint.py`
- `tests/characterization/test_boards.py`
- `tests/characterization/test_cards.py`
- `tests/characterization/test_lists.py`
- `tests/characterization/test_authentication.py`
- `tests/characterization/test_api.py`
- `tests/doubles/fake_trello_client.py`
- `tests/doubles/fake_clock.py`

Keep each module focused on one responsibility. Do not create a monolithic handler or test file.

Internal modules must import concrete modules. They must not import package facades, index modules, or coordinator entrypoints.

## Public Contracts

### Django check command

Run `python manage.py check` from the repository root.

Use Python 3.12 or later and Django 5.x. Return exit status `0` when checks pass.

Write exactly `System check identified no issues (0 silenced).` to standard output on success.

Write no error line to standard error on success.

Return a non-zero status on failure. Write an error whose first standard error line starts with `djanban error:`.

### Health endpoint

Expose `GET /healthz`.

Return status `200`, content type `application/json`, and compact body `{"status":"ok"}`.

Accept a missing `Accept` header. Ignore a request body on `GET`.

Return status `405` for non-GET methods. Return status `404` for unknown paths.

Do not expose a stack trace in error responses.

### Legacy routes

Use existing routes from `src/djanban/apps/api/urls.py` and their view modules.

Preserve paths, methods, status codes, authentication rules, field names, envelopes, pagination, content types, and validation errors.

Use `Content-Type: application/json` for JSON requests. Reject malformed JSON with the characterized legacy status and envelope.

Do not convert malformed JSON into an empty request.

## Characterization Requirements

Observe legacy behavior before refactoring it. Add a failing test before changing covered behavior.

Characterize board creation, retrieval, update, deletion, listing, permissions, empty results, and invalid identifiers.

Characterize card creation, retrieval, update, deletion, movement, member assignment, due dates, missing cards, invalid board references, blank titles, long titles, missing lists, and duplicate submissions.

Characterize list creation, retrieval, update, deletion, ordering, movement, empty lists, invalid board references, duplicate names, blank names, negative positions, and large positions.

Characterize anonymous access, valid login, invalid login, logout, sessions, protected pages, protected API routes, and missing or expired credentials.

Characterize API methods, path parameters, query parameters, request validation, response envelopes, pagination, content types, authentication, malformed JSON, extra fields, unsupported methods, and errors.

Use exact JSON comparisons for stable fields. Ignore only documented volatile fields.

## Test Doubles

Implement `FakeTrelloClient` in `tests/doubles/fake_trello_client.py`.

Store boards, lists, cards, and members in memory. Support deterministic reads and writes. Raise explicit test errors for unknown identifiers.

Implement `FakeClock` in `tests/doubles/fake_clock.py`.

Return a caller-selected instant. Use it for every test that checks timestamps, expiry, ordering, or session age.

Do not call Trello, email, payment, filesystem, or other network services from tests.

## Scenario and Edge Case Matrix

| Area | Input or action | Expected result |
|---|---|---|
| Boot | Python 3.12 and Django 5.x | The check command returns `0`. |
| Boot | Missing required setting | The command returns non-zero and prefixes stderr with `djanban error:`. |
| Health | `GET /healthz` | Return `200` and `{"status":"ok"}`. |
| Health | `POST /healthz` | Return `405` without a stack trace. |
| Health | Unknown path | Return `404` without a stack trace. |
| Health | Missing `Accept` header | Return the health contract. |
| Health | Body on `GET` | Ignore the body and return the health contract. |
| Authentication | Anonymous protected request | Return the characterized redirect or JSON error. |
| Authentication | Valid credentials | Permit the characterized operation. |
| Authentication | Invalid credentials | Reject access with the legacy contract. |
| Authentication | Logout then protected request | Reject access after logout. |
| Board | Valid, unknown, or malformed identifier | Return the characterized response. |
| Board | Empty collection | Return the characterized empty response. |
| Card | Blank title, long title, missing list, or invalid board | Return the characterized validation response. |
| Card | Duplicate submission | Preserve the characterized status and data behavior. |
| List | Blank or duplicate name | Return the characterized validation response. |
| List | Negative or large position | Preserve the characterized validation and ordering behavior. |
| API | Malformed JSON | Return the characterized client error envelope. |
| API | Unsupported method | Return `405` and allowed method information when present. |
| API | Extra JSON fields | Preserve characterized acceptance or rejection. |
| Test system | Network unavailable | All tests pass without network access. |
| Test system | Fixed clock instant | Time assertions remain deterministic. |

## Definition of Done (DoD)

- [ ] Create every required file listed in this story.
- [ ] Keep `manage.py` below 15 executable lines.
- [ ] Delegate immediately from `manage.py` to `django.core.management.execute_from_command_line`.
- [ ] Set `DJANGO_SETTINGS_MODULE` to `djanban.settings` in management and WSGI entrypoints.
- [ ] Keep `djanban/wsgi.py` focused on WSGI application creation.
- [ ] Keep `djanban/health.py` focused on the health response.
- [ ] Use environment variables for secrets and deployment settings.
- [ ] Provide safe local defaults for tests.
- [ ] Configure an in-memory SQLite test database.
- [ ] Expose `GET /healthz` with the exact status, content type, and compact JSON body.
- [ ] Return controlled `404` and `405` responses without stack traces.
- [ ] Preserve characterized board, card, list, authentication, and API contracts.
- [ ] Use Chicago-school tests against real Django request handling and real domain objects.
- [ ] Inject external boundaries and use the in-memory Trello client in tests.
- [ ] Use the fake clock for every time or expiry assertion.
- [ ] Add one runnable black-box E2E scenario for `GET /healthz`.
- [ ] Add dedicated runnable characterization scenarios for board, card, list, authentication, and API capabilities.
- [ ] Execute E2E HTTP requests against the running application.
- [ ] Poll socket readiness instead of using static sleep delays.
- [ ] Set a maximum timeout of 2 seconds for every HTTP, socket, and network read in tests.
- [ ] Assert response payloads, status codes, headers, authentication behavior, and error formats.
- [ ] Run `python manage.py check` with exit status `0` on success.
- [ ] Run `python -m pytest -q` with zero failures and zero collection errors.
- [ ] Run `ruff check .` with status `0`.
- [ ] Run `mypy --strict .` with status `0`.
- [ ] Do not require zero-linter-error gates for later feature stories; treat their lint results as advisory.
- [ ] Do not use Python below 3.12 or Django below 5.0.
- [ ] Do not add AngularJS behavior or dependencies.
- [ ] Do not add network calls, production credentials, live external databases, or live brokers to tests.
- [ ] Do not use `pass`, ellipsis placeholders, `NotImplementedError`, broad exception masking, skipped tests, or `|| true`.
- [ ] Do not place analytics logic in Django views.
- [ ] Do not delete legacy files before characterization coverage exists.
- [ ] Ask whether a Python script provides a safer method for each structured-data edit.
- [ ] Keep internal imports acyclic and free from package facade imports.
- [ ] Verify every scenario matrix row with an automated test.
- [ ] Do not implement analytics owned by US-002, US-003, or US-004.

## Verification Commands

Run these commands from the repository root:

```text
python --version
python -m django --version
python manage.py check
ruff check .
mypy --strict .
python -m pytest -q
```

Require exit status `0` from every command. Do not mask failures.

## Acceptance Criteria

1. Create the modern entrypoint at every required path.
2. Verify Python 3.12 or later and Django 5.x.
3. Verify the exact successful check output.
4. Verify the exact health response and negative method behavior.
5. Verify characterization coverage for boards, cards, lists, authentication, and APIs.
6. Verify in-memory SQLite, offline test doubles, and deterministic clocks.
7. Verify dedicated black-box scenarios for every capability in this story.
8. Verify zero test failures and zero collection errors.
9. Verify no forbidden stub, placeholder, dependency, or error masking remains.
10. Verify that later analytics features remain outside this story.

## Machine Contract

```noctifab-contract
{
  "story_id": "US-001",
  "public_contracts": [
    {
      "id": "healthz-http-get",
      "interface": "HTTP GET /healthz",
      "applicable_path_prefixes": ["djanban/", "tests/"],
      "allowed_executables": ["python", "python -m pytest"],
      "exit_codes": [0, 1],
      "stdout_contains": ["{\\"status\\":\\"ok\\"}"],
      "stderr_prefixes": ["djanban error:"]
    },
    {
      "id": "django-check-command",
      "interface": "CLI python manage.py check",
      "applicable_path_prefixes": ["manage.py", "djanban/"],
      "allowed_executables": ["python"],
      "exit_codes": [0, 1],
      "stdout_contains": ["System check identified no issues (0 silenced)."],
      "stderr_prefixes": ["djanban error:"]
    }
  ]
}
```