# -*- coding: utf-8 -*-

import os

# Authentication configuration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "../resources/database/djangotrellostats.db")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = u'sdfjasñldfkjsadflñkasjdfksdjf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = "localhost"
ALLOWED_HOSTS = [DOMAIN]
PORT = "80"
if DEBUG is True and DOMAIN == "localhost":
    PORT = "8000"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATABASE_PATH,
        'HOST': '',
        'PORT': ''
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Europe/Madrid"

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'djangotrellostats@gmail.com'
EMAIL_HOST_PASSWORD = 'xxx'
DEFAULT_FROM_EMAIL = 'djangotrellostats@gmail.com'