#! /bin/bash

if [ ! -f ./src/djangotrellostats/settings_local.py ]; then
    cp ./src/djangotrellostats/settings_local.dply.py ./src/djangotrellostats/settings_local.py
fi

./venv/bin/python ./src/manage.py migrate

./venv/bin/python ./src/manage.py runserver
