# Upgrade Notes for Djanban

This repository has been upgraded to support **Python 3.10+** and **Django 5.0+**.
The frontend (Angular) requires additional manual steps to fully migrate to the latest Angular version.

## Backend Changes

The following changes were applied to the Python/Django codebase:

1.  **Dependencies**: `requirements.txt` was updated to use `Django>=5.0` and other modern libraries. Python 2 specific libraries (`enum34`, `ipaddress`, etc.) were removed.
2.  **Imports**: 
    *   Removed `from __future__` imports.
    *   Updated `django.conf.urls.url` to `django.urls.re_path`.
    *   Updated `django.core.urlresolvers.reverse` to `django.urls.reverse`.
    *   Updated `ugettext` and `ugettext_lazy` to `gettext` and `gettext_lazy`.
3.  **Settings**:
    *   Replaced `MIDDLEWARE_CLASSES` (deprecated) with `MIDDLEWARE` in `djanban/settings.py`.
4.  **URLs**:
    *   Added `app_name` variable to `urls.py` files in all apps to support namespaced `include()`, which is required in newer Django versions.

### Required Actions (Backend)

*   **Virtual Environment**: Create a new Python 3 virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r src/requirements.txt
    ```
*   **Database**: Run migrations to ensure the database schema is up to date (though no model changes were made by the agent).
    ```bash
    cd src
    python manage.py migrate
    ```

## Frontend Changes (Angular)

The Angular application located in `src/djanban/static/angularapps/taskboard` is currently on **Angular 2.4.5** using **SystemJS**.
Modern Angular (v18/19+) uses **Webpack** or **Vite** via the Angular CLI and has a significantly different build process and API (e.g., `HttpClient` instead of `Http`, removal of `SystemJS`).

**Automatic upgrade of the frontend was not performed** because it requires a complete restructuring of the build system and manual porting of code, which carries a high risk of breakage without a working test environment.

### Recommended Migration Path for Frontend

1.  **Install Angular CLI**: `npm install -g @angular/cli`
2.  **Create a New App**: Create a new Angular app alongside the old one.
    ```bash
    ng new taskboard-v2
    ```
3.  **Port Components**: Manually copy your components from `src/djanban/static/angularapps/taskboard/app` to the new project.
    *   Replace `@angular/http` usage with `@angular/common/http`.
    *   Replace `System.import` with dynamic imports.
    *   Update RxJS syntax (pipes).
4.  **Replace Old App**: Once ported, build the new app using `ng build` and point your Django static files to the new build output.

## Running the App

After setting up the virtual environment:

```bash
cd src
python manage.py runserver
```
