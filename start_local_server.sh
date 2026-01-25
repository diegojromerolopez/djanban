#! /bin/bash

# Ensure .venv exists
if [ ! -d .venv ]; then
    uv venv --python 3.14
    uv pip install -r src/requirements.txt
fi

# Ensure settings_local.py exists
if [ ! -f ./src/djanban/settings_local.py ]; then
    cp ./src/djanban/settings_local.runserver.py ./src/djanban/settings_local.py
fi

# Migrate and run
uv run src/manage.py migrate
uv run src/manage.py runserver --insecure
