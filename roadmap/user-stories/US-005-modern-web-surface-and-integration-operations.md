# US-005: Modern Web Surface and Integration Operations

## Story

As a board user, I want a secure modern web surface, so I can manage boards, lists, and cards without AngularJS.

## Metadata

- Story ID: `US-005`
- Slug: `US-005-modern-web-surface-and-integration-operations`
- Domain capability: Django REST API, authentication, authorization, CSRF, and AngularJS retirement
- Complexity: 25 CU
- Depends on: `[]`
- Change type: `new`
- Runtime: Python 3.12 or newer
- Framework: Django 5.x
- API style: Django REST Framework with versioned JSON routes

## Requirements

Create one stable HTTP surface under `/api/v1/`. Use Django REST Framework serializers for all public request and response bodies. Keep domain calculators outside HTTP handlers. Delegate analytics calculations to US-002, US-003, and US-004 services.

Register these routes with trailing slashes:

- `GET` and `POST` `/api/v1/boards/`
- `GET`, `PATCH`, and `DELETE` `/api/v1/boards/{board_id}/`
- `GET` and `POST` `/api/v1/boards/{board_id}/lists/`
- `GET`, `PATCH`, and `DELETE` `/api/v1/lists/{list_id}/`
- `GET` and `POST` `/api/v1/boards/{board_id}/cards/`
- `GET`, `PATCH`, and `DELETE` `/api/v1/cards/{card_id}/`
- `GET` and `POST` `/api/v1/boards/{board_id}/members/`
- `DELETE` `/api/v1/boards/{board_id}/members/{member_id}/`
- `GET` `/api/v1/boards/{board_id}/wip-status/`
- `GET` `/api/v1/boards/{board_id}/regressions/`
- `GET` `/api/v1/boards/{board_id}/time-tracking/`
- `GET` `/api/v1/boards/{board_id}/lead-cycle-times/`
- `GET` `/api/v1/boards/{board_id}/schedule-status/`

Use Django session authentication and bearer authentication. Read bearer credentials from `Authorization: Bearer <token>`. Never log credentials. Require authentication for every API route except the documented health route.

Allow owners to manage boards and membership. Allow members to read boards, lists, cards, members, and analytics. Apply object-level checks to every list and card operation. Return `404 not_found` for inaccessible objects when disclosure creates a risk.

Require CSRF tokens for session-authenticated `POST`, `PUT`, `PATCH`, and `DELETE` requests. Accept the `X-CSRFToken` header and the configured form field. Do not exempt API views from CSRF middleware. Apply the documented bearer-token policy without browser-session inheritance.

Return collection bodies as `{"results": [], "count": 0}`. Return resource objects for single-resource operations. Return UTC timestamps with a `Z` suffix. Return JSON numbers, not numeric strings. Reject unknown writable fields. Reject blank required strings, negative positions, invalid identifiers, invalid WIP bounds, malformed JSON, and unsupported media types.

Use this error body for every JSON error:

`{"error":{"code":"<STABLE_CODE>","message":"<SAFE_MESSAGE>","field_errors":{}}}`

Use these error codes: `invalid_json`, `invalid_request`, `authentication_required`, `authentication_failed`, `permission_denied`, `csrf_failed`, `not_found`, `method_not_allowed`, `unsupported_media_type`, `unsupported_format`, and `internal_error`.

Return these headers on JSON responses:

- `Content-Type: application/json`
- `X-Content-Type-Options: nosniff`
- `Cache-Control: no-store` for authenticated responses

Provide `/boards/`, `/boards/{board_id}/`, and `/login/` when the HTML surface exists. Return HTML only for HTML requests. Redirect anonymous browser requests safely to `/login/`. Remove active AngularJS scripts, modules, routes, templates, build references, and served files. Preserve legacy files only when no active code serves, imports, builds, or references them.

## Required implementation paths

Create or modify each path below. Keep each module focused on one responsibility. Keep imports directed toward leaf modules. Do not import handlers or submodules through package facade modules.

- `src/manage.py`
- `src/djanban/settings.py`
- `src/djanban/urls.py`
- `src/djanban/api/__init__.py`
- `src/djanban/api/urls.py`
- `src/djanban/api/authentication.py`
- `src/djanban/api/permissions.py`
- `src/djanban/api/exceptions.py`
- `src/djanban/api/renderers.py`
- `src/djanban/api/serializers/__init__.py`
- `src/djanban/api/serializers/boards.py`
- `src/djanban/api/serializers/lists.py`
- `src/djanban/api/serializers/cards.py`
- `src/djanban/api/serializers/members.py`
- `src/djanban/api/serializers/analytics.py`
- `src/djanban/api/views/__init__.py`
- `src/djanban/api/views/boards.py`
- `src/djanban/api/views/lists.py`
- `src/djanban/api/views/cards.py`
- `src/djanban/api/views/members.py`
- `src/djanban/api/views/analytics.py`
- `src/djanban/web/__init__.py`
- `src/djanban/web/urls.py`
- `src/djanban/web/views.py`
- `src/djanban/templates/boards/index.html`
- `src/djanban/templates/boards/detail.html`
- `src/djanban/templates/registration/login.html`

## Required test paths

- `tests/unit/api/test_authentication.py`
- `tests/unit/api/test_permissions.py`
- `tests/unit/api/test_serializers.py`
- `tests/unit/api/test_csrf.py`
- `tests/integration/api/test_routes.py`
- `tests/integration/api/test_board_api.py`
- `tests/integration/api/test_list_api.py`
- `tests/integration/api/test_card_api.py`
- `tests/integration/api/test_member_api.py`
- `tests/integration/api/test_analytics_api.py`
- `tests/integration/web/test_rendered_views.py`
- `tests/e2e/test_http_surface.py`
- `tests/e2e/test_angular_retirement.py`

Use `InMemoryBoardRepository`, `InMemoryListRepository`, `InMemoryCardRepository`, `InMemoryMemberRepository`, `FakeTokenStore`, and `FakeTrelloClient`. Inject each boundary. Use SQLite `:memory:` for integration tests. Use a fixed UTC clock for every timestamp assertion. Ask whether a Python script provides a safer method before editing JSON, TOML, fixtures, or other structured data.

## Definition of Done (DoD)

### Public interfaces

- Expose every route listed in this story under `/api/v1/`.
- Expose the optional HTML routes with Django templates.
- Keep `src/manage.py` as a thin wrapper under 15 lines that delegates to Django.
- Serialize board fields as `id`, `name`, `owner_id`, `created_at`, and `updated_at`.
- Serialize list fields as `id`, `board_id`, `name`, `position`, `min_wip`, and `max_wip`.
- Serialize card fields as `id`, `board_id`, `list_id`, `title`, `description`, `position`, `created_at`, and `updated_at`.
- Serialize member fields as `id`, `username`, `display_name`, and `role`.
- Preserve exact analytics field names, enum values, and two-decimal numeric values from owning stories.

### HTTP and output rules

- Return `200` for successful reads and updates.
- Return `201` for successful creates.
- Return `204` for successful deletes without a body.
- Return `400` for invalid JSON and invalid fields.
- Return `401` for missing or invalid authentication.
- Return `403` for permission or CSRF failures.
- Return `404` for unknown or inaccessible resources.
- Return `405` for unsupported methods.
- Return `406` for unsupported response formats.
- Return `415` for unsupported media types.
- Return `500` only through the safe `internal_error` envelope.
- Return `field_errors: {}` when no field error exists.
- Return empty collections with `results: []` and `count: 0`.
- Return no traceback, secret, token, database detail, or file path.
- Require `Content-Type: application/json` for JSON requests.
- Require `Accept: application/json` for API requests.
- Set `X-Content-Type-Options: nosniff` on JSON responses.
- Set `Cache-Control: no-store` on authenticated JSON responses.
- Prefix startup failures with `djanban startup error:`.
- Prefix configuration failures with `djanban configuration error:`.
- Return process status `0` after successful checks and non-zero status after failures.

### Scenario and edge-case matrix

Test each scenario with real serializers, views, middleware, repositories, and domain objects:

| Scenario | Expected result |
|---|---|
| Health route with a safe request | Return the US-001 health contract with `200`. |
| Unauthenticated API read | Return `401 authentication_required`. |
| Unknown bearer token | Return `401 authentication_failed`. |
| Expired bearer token | Return `401 authentication_failed`. |
| Member reads own board | Return only visible data with `200`. |
| Caller reads a foreign board | Return `404 not_found` or the documented `403`. |
| Owner creates a board | Return `201` and a complete board resource. |
| Missing `name` | Return `400 invalid_request` with field errors. |
| Blank `name` | Return `400 invalid_request`. |
| Unknown writable field | Return `400 invalid_request` and write no state. |
| Malformed JSON | Return `400 invalid_json`. |
| XML or plain text body | Return `415 unsupported_media_type`. |
| Unsupported method | Return `405 method_not_allowed`. |
| Invalid identifier | Return the documented `400` or `404` result. |
| Duplicate resource name | Return a stable validation error and write no partial state. |
| Negative position | Return `400 invalid_request`. |
| `min_wip > max_wip` | Return `400 invalid_request`. |
| Empty board collection | Return `200` with an empty collection envelope. |
| Valid session write with CSRF token | Complete the write successfully. |
| Session write without CSRF token | Return `403 csrf_failed`. |
| Session write with an invalid CSRF token | Return `403 csrf_failed`. |
| Safe session read without CSRF token | Complete the read when authorized. |
| Bearer request with browser session state | Apply bearer authentication only. |
| Member deletes a board | Return `403 permission_denied` and preserve state. |
| Stale update version | Return `409` with a stable conflict envelope when versioning exists. |
| Injected repository failure | Return `500 internal_error` without a traceback. |
| Authenticated HTML request | Return `200` HTML without AngularJS markers. |
| Anonymous HTML request | Redirect safely to `/login/`. |
| Active AngularJS marker | Fail the retirement test. |

### Black-box verification

- Run `python src/manage.py check`.
- Run `pytest -q tests/unit tests/domain`.
- Run `pytest -q tests/integration`.
- Run `pytest -q tests/e2e`.
- Run `pytest -q`.
- Poll the local socket for readiness. Do not use a static sleep.
- Set a maximum two-second timeout for every HTTP request, socket connection, and network read.
- Execute a dedicated E2E scenario for board list, board create, board read, board update, board delete, list operations, card operations, member operations, and each analytics endpoint.
- Assert response headers, response bodies, authorization scope, error envelopes, numeric formats, and database state.
- Assert every authentication, authorization, CSRF, media type, method, identifier, validation, HTML, and AngularJS retirement case.
- Use Chicago-school tests that observe state transitions. Do not use tautological tests, generic imports, or status-only assertions.
- Require a 100 percent pass rate for unit, integration, and black-box E2E suites.
- Treat lint findings as advisory for this feature story. Reserve zero-error Ruff and strict Mypy gates for US-006.
- Do not use AngularJS, live Trello services, live external databases, live queues, or live network services in unit or integration tests.
- Do not use the forbidden legacy `docker-compose` command. No Docker Compose harness is required by this story.
- Do not add stubs, placeholders, `pass`, ellipses, `NotImplementedError`, fake success responses, blanket CSRF exemptions, permissive authentication defaults, or error-masking shell commands.

```noctifab-contract
{
  "story_id": "US-005",
  "public_contracts": [
    {
      "id": "http-api-v1",
      "interface": "HTTP JSON API at /api/v1/",
      "applicable_path_prefixes": ["src/djanban/api/", "tests/integration/api/", "tests/e2e/"],
      "allowed_executables": ["python src/manage.py check", "python src/manage.py runserver 127.0.0.1:8000", "pytest -q tests/e2e"],
      "exit_codes": [0],
      "stdout_contains": ["passed"],
      "stderr_prefixes": ["djanban startup error:", "djanban configuration error:"]
    },
    {
      "id": "json-error-envelope",
      "interface": "HTTP JSON error response",
      "applicable_path_prefixes": ["src/djanban/api/", "tests/integration/api/", "tests/e2e/"],
      "allowed_executables": ["pytest -q tests/integration/api/test_routes.py", "pytest -q tests/e2e/test_http_surface.py"],
      "exit_codes": [0],
      "stdout_contains": ["error", "code", "message", "field_errors"],
      "stderr_prefixes": ["djanban startup error:", "djanban configuration error:"]
    }
  ]
}
```