# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import importlib
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from trello.organization import Organization

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR+"/djangotrellostats/media"

#
settings_local_module = 'djangotrellostats.settings_local'
if os.environ.get("DJANGO_APP_MODE") == "desktop_app":
    settings_local_module = 'djangotrellostats.settings_desktop_app'

try:
    settings_local = importlib.import_module(settings_local_module)
except ImportError:
    print("Please, create a {0} in project directory with SECRET_KEY, DEBUG, DOMAIN, ALLOWED_HOSTS and DATABASES settings".format(settings_local_module))
    exit(-1)

print settings_local_module

DATABASES = settings_local.DATABASES

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings_local.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings_local.DEBUG

DOMAIN = settings_local.DOMAIN
ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS

SITE_ID = 1

# Administrator group
ADMINISTRATOR_GROUP = "Administrators"

DATE_INPUT_FORMATS = ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y')

# Application definition

INSTALLED_APPS = [
    'captcha',
    'ckeditor',
    'ckeditor_uploader',
    'crequest',
    'cuser',
    'dal',
    'dal_select2',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'djangotrellostats.apps.agility_rating',
    'djangotrellostats.apps.base',
    'djangotrellostats.apps.boards',
    'djangotrellostats.apps.charts',
    'djangotrellostats.apps.hourly_rates',
    'djangotrellostats.apps.index',
    'djangotrellostats.apps.journal',
    'djangotrellostats.apps.dev_times',
    'djangotrellostats.apps.dev_environment',
    'djangotrellostats.apps.fetch',
    'djangotrellostats.apps.members',
    'djangotrellostats.apps.niko_niko_calendar',
    'djangotrellostats.apps.reporter',
    'djangotrellostats.apps.reports',
    'djangotrellostats.apps.repositories',
    'djangotrellostats.apps.requirements',
    'djangotrellostats.apps.slideshow',
    'djangotrellostats.apps.visitors',
    'djangotrellostats.apps.workflows',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'crequest.middleware.CrequestMiddleware',
    'cuser.middleware.CuserMiddleware'
)

ROOT_URLCONF = 'djangotrellostats.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+"/djangotrellostats/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases



# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.member.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.member.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.member.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.member.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = settings_local.LANGUAGE_CODE

TIME_ZONE = settings_local.TIME_ZONE
Organization.TIMEZONE = TIME_ZONE

if hasattr(settings_local, "DATE_FORMAT"):
    DATE_FORMAT = settings_local.DATE_FORMAT
else:
    DATE_FORMAT = "Y-m-d"

if hasattr(settings_local, "DATETIME_FORMAT"):
    DATETIME_FORMAT = settings_local.DATETIME_FORMAT
else:
    DATETIME_FORMAT = "Y-m-d H:i"



USE_I18N = False

USE_L10N = False

USE_TZ = True

LOGIN_URL = '/base/login/'

EMAIL_USE_TLS = settings_local.EMAIL_USE_TLS
EMAIL_HOST = settings_local.EMAIL_HOST
EMAIL_PORT = settings_local.EMAIL_PORT
EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL

# HTTPS configuration
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = False  # Django >= 1.4
USE_X_FORWARDED_PORT = False
SECURE_SSL_REDIRECT = False
SECURE_SSL_HOST = None


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATICFILES_DIRS = [
    BASE_DIR + "/djangotrellostats/static/"
]

TMP_DIR = BASE_DIR + "/djangotrellostats/tmp/"

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR + "/public_html/collectedstatic"

# CKEDITOR preferences
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_RESTRICT_BY_USER = False
CKEDITOR_BROWSE_SHOW_DIRS = True

CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Image', 'Update', 'Link', 'Unlink'],
            ['RemoveFormat'],
        ],
    },
    'basic': {
        'toolbar': 'basic'
    },
    'full': {
        'toolbar': 'full'
    }
}
