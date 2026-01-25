# -*- coding: utf-8 -*-
SECRET_KEY = "test_secret_key"
DEBUG = True
DOMAIN = "localhost"
PORT = 8000
ALLOWED_HOSTS = [DOMAIN]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "djanban.db",
    }
}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
EMAIL_USE_TLS = False
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "webmaster@localhost"
SERVER_EMAIL = "root@localhost"
