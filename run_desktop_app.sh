#!/bin/bash

# Operative System detection
uname_output=`uname`

# Absolute paths
ROOT_DIR=`dirname "$BASH_SOURCE"`
SRC_DIR="$ROOT_DIR/src"

# Name of the virtualnenv name
VENV_NAME="venv.desktop_app"

# Creation of virtualenv
if ! [ -d "$ROOT_DIR/$VENV_NAME" ]; then
    virtualenv "$ROOT_DIR/$VENV_NAME" -p /usr/bin/python
fi

# Installing of Python packages
$ROOT_DIR/$VENV_NAME/bin/pip install -r $SRC_DIR/requirements.desktop_app.txt

# Creation of empty SQLite database if needed
if ! [ -f "$ROOT_DIR/resources/database/djangotrellostats.db" ]; then
    echo "" > "$ROOT_DIR/resources/database/djangotrellostats.db"
fi

# Executing Django migrations
$ROOT_DIR/$VENV_NAME/bin/python $SRC_DIR/desktop_app_manage.py migrate

# OS dependant configurations
if [[ $OSTYPE == darwin* ]]; then
    if ! [ -d "$ROOT_DIR/$VENV_NAME/.Python.app" ]; then
        sudo "$ROOT_DIR/$VENV_NAME/bin/fix-osx-virtualenv" "$ROOT_DIR/$VENV_NAME"
        sudo chown -R $USER "$ROOT_DIR/$VENV_NAME"
    fi
fi

# Finally, running the app
$ROOT_DIR/$VENV_NAME/bin/python $SRC_DIR/desktop_app_main.py