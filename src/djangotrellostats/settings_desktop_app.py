# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import importlib
import os
import sqlite3

DOMAIN = "localhost"
ALLOWED_HOSTS = [DOMAIN]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "djangotrellostats/db/djangotrellostats.db")

# Create database if not exists
if not os.path.isfile(DATABASE_PATH):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.close()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_PATH,
        'HOST': '',
        'PORT': ''
    }
}

try:
    settings_local = importlib.import_module("djangotrellostats.settings_local_desktop_app")
except ImportError:
    print("Please, create a settings_local_desktop_app.py in project directory with SECRET_KEY, DEBUG, DOMAIN, ALLOWED_HOSTS and DATABASES settings")
    exit(-1)

DEBUG = settings_local.DEBUG

SECRET_KEY = settings_local.SECRET_KEY

LANGUAGE_CODE = settings_local.LANGUAGE_CODE
TIME_ZONE = settings_local.TIME_ZONE

EMAIL_USE_TLS = settings_local.EMAIL_USE_TLS
EMAIL_HOST = settings_local.EMAIL_HOST
EMAIL_PORT = settings_local.EMAIL_PORT
EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL