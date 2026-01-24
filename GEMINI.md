# Djanban Project Guide

## Project Overview

**Djanban** is a Kanban board application that offers statistical analysis and charting capabilities. It supports optional integration with Trello to fetch data from boards for processing and visualization. The application aids in strategic decision-making by tracking work in progress, lead/cycle times, and team work hours.

### Current Status
- **Django Version**: 1.11
- **Python Version**: 2.7 (Inferred from dependencies like `enum34`, `pathlib2`)

## Folder Structure

The project follows a standard Django structure within a `src` directory:

- **root**
    - `start_local_server.sh`: Script to start the local development server.
    - `src/`
        - `manage.py`: Django's command-line utility.
        - `requirements.txt`: Project dependencies (to be migrated).
        - `djanban/`
            - `settings.py`: Main configuration.
            - `urls.py`: Main URL routing.
            - `apps/`: Modular Django applications:
                - **Core Features**:
                    - `boards`: Core business logic (Boards, Lists, Cards, Labels).
                    - `members`: User management and roles.
                    - `fetch`: Logic for syncing data from Trello (commands and fetchers).
                    - `multiboards`: Functionality to group multiple boards.
                    - `workflows`: Board process definitions and workflow stats.
                - **Analytics & Reporting**:
                    - `charts`: Caching and rendering logic for charts.
                    - `reports`: Detailed analytics like Card Movements and Reviews.
                    - `reporter`: Automated reporting tools (daily/weekly emails).
                    - `forecasters`: Project forecasting models.
                    - `agility_rating`: Project agility scoring.
                - **Developer Metrics**:
                    - `dev_environment`: Environment tracking (interruptions, noise).
                    - `dev_times`: Time tracking and daily spent time.
                    - `hourly_rates`: Cost analysis based on hourly rates.
                    - `journal`: Developer work logs.
                    - `niko_niko_calendar`: Team mood tracking.
                    - `work_hours_packages`: Time budget management.
                - **Code Quality**:
                    - `repositories`: Git integration and code quality metrics (Pylint, PHPMD).
                    - `requirements`: Requirements traceability.
                - **Utilities**:
                    - `anonymizer`: Data scrubbing for privacy.
                    - `api`: REST API implementation.
                    - `base`: Core utilities (Auth, Email, Base Templates).
                    - `destructor`: Data cleanup tools.
                    - `index`: Main dashboard views.
                    - `notifications`: User alert system.
                    - `password_reseter`: Password recovery flow.
                    - `recurrent_cards`: Task automation for repeating cards.
                    - `slideshow`: Kiosk/presentation mode.
                    - `visitors`: Public or guest access handling.

## Upgrade Strategy

The modernization of this legacy codebase must follow a strict, safe path to ensure no regression in functionality.

1.  **Establish Test Coverage**: Before any code changes, create a comprehensive test suite capturing the current behavior. Use the existing codebase behavior as the source of truth.
2.  **Upgrade Python**: Migrate the codebase to run on **Python 3.14**.
    - This will likely involve using tools like `2to3` or `pyupgrade` initially, but manual verification via tests is paramount.
3.  **Upgrade Django**: Once running on Python 3.14, upgrade the Django version step-by-step (e.g., 1.11 -> 2.0 -> 2.2 -> 3.2 -> 4.2 -> 5.x).
    - Fix deprecation warnings at each step.
    - Verify with tests at each step.

## Development Methodology

### TDD (Test-Driven Development)
All development must follow the TDD cycle:
1.  **Red**: Write a failing test for the desired feature or bug fix.
2.  **Green**: Write the minimal "draft" implementation to pass the test. This implementation creates the necessary headers/interfaces but does not need to be perfect.
3.  **Refactor**: Clean up the code, applying patterns and standards, while ensuring tests remain green.

### Coding Standards
- **Active Record Pattern**: Utilize Django's ORM effectively.
- **SOLID Principles**: Ensure classes and functions have single responsibilities and loose coupling.
- **Single-Statement Assignment**: Avoid complex one-liners; prioritize readability.
- **Type Hinting**: Extensive use of Python type hints (PEP 484) for all function signatures and variable declarations.

### Linters & Quality Tools
The project enforces strict code quality using the following tools:
- **black**: For uncompromising code formatting.
- **flake8**: For style guide enforcement.
- **isort**: For sorting imports.
- **mypy**: For static type checking.
- **pylint**: For code analysis and error detection.
- **ruff**: For fast linting and modernizing code.

## Dependency Management

1.  **Fix `requirements.txt`**: Audit the current `requirements.txt` to identify packages that are incompatible with Python 3.
2.  **Move to `uv`**: Adopt `uv` for extremely fast pip interface and dependency management.
    - Initialize the project with `uv` (or `rye` if preferred wrapper is needed, but `uv` is the target).
    - Generate a locked dependency file (e.g., `uv.lock` or standard `requirements.lock`).

## Recommendations for Onboarding & Best Practices

To ensure the easiest onboarding for seasoned Python developers:

- **Environment Variables**: Use `python-dotenv` or `django-environ` to manage configuration (Database credentials, API keys) via `.env` files, keeping them out of source control.
- **Virtual Environments**: Always develop within an isolated virtual environment (`.venv`).
- **Pre-commit Hooks**: Set up `pre-commit` to automatically run `black`, `isort`, `flake8`, and `ruff` on every commit.
- **Docker**: (Optional but recommended) logical next step is to containerize the application and database for a consistent development environment (`docker-compose`).
- **Documentation**: Keep extensive docstrings using the Google or Sphinx style.
