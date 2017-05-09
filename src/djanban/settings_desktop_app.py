# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import importlib
import os
import sqlite3

DOMAIN = "localhost"
ALLOWED_HOSTS = [DOMAIN]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "../resources/database/djanban.db")

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
    settings_local_desktop_app = importlib.import_module("djanban.settings_local_desktop_app")
except ImportError:
    print("Please, create a settings_local_desktop_app.py in project directory with SECRET_KEY, DEBUG, DOMAIN, ALLOWED_HOSTS and DATABASES settings")
    exit(-1)

DEBUG = settings_local_desktop_app.DEBUG

SECRET_KEY = settings_local_desktop_app.SECRET_KEY

LANGUAGE_CODE = settings_local_desktop_app.LANGUAGE_CODE
TIME_ZONE = settings_local_desktop_app.TIME_ZONE

if hasattr(settings_local_desktop_app, "DATE_FORMAT"):
    DATE_FORMAT = settings_local_desktop_app.DATE_FORMAT
else:
    DATE_FORMAT = "Y-m-d"

if hasattr(settings_local_desktop_app, "DATETIME_FORMAT"):
    DATETIME_FORMAT = settings_local_desktop_app.DATETIME_FORMAT
else:
    DATETIME_FORMAT = "Y-m-d H:i"

EMAIL_USE_TLS = settings_local_desktop_app.EMAIL_USE_TLS
EMAIL_HOST = settings_local_desktop_app.EMAIL_HOST
EMAIL_PORT = settings_local_desktop_app.EMAIL_PORT
EMAIL_HOST_USER = settings_local_desktop_app.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local_desktop_app.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = settings_local_desktop_app.DEFAULT_FROM_EMAIL