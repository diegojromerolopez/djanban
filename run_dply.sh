#! /bin/bash

# Make sure we have the needed packages installed
sudo apt-get -y install git python python-dev virtualenv build-essential libssl-dev libffi-dev libmysqlclient-dev libxml2-dev libxslt1-dev

if [ ! -d ./src/venv ]; then
    virtualenv venv
    ./venv/bin/pip install -r ./src/requirements.txt
fi

if [ ! -f ./src/djangotrellostats/settings_local.py ]; then
    cp ./src/djangotrellostats/settings_local.dply.py ./src/djangotrellostats/settings_local.py
fi

./venv/bin/python ./src/manage.py migrate

./venv/bin/python ./src/manage.py runserver
