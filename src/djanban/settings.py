# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import importlib
import os
import pytz

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from trello.organization import Organization

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR+"/djanban/media"

#
settings_local_module = 'djanban.settings_local'
if os.environ.get("DJANGO_APP_MODE") == "desktop_app":
    settings_local_module = 'djanban.settings_desktop_app'

try:
    settings_local = importlib.import_module(settings_local_module)
except ImportError:
    print("Please, create a {0} in project directory with SECRET_KEY, DEBUG, DOMAIN, ALLOWED_HOSTS and DATABASES settings".format(settings_local_module))
    exit(-1)

DATABASES = settings_local.DATABASES

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings_local.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings_local.DEBUG

DOMAIN = settings_local.DOMAIN
PORT = settings_local.PORT
ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS

ADMINS = []
if hasattr(settings_local, "ADMINS"):
    ADMINS = settings_local.ADMINS

SITE_ID = 1

# Administrator group
ADMINISTRATOR_GROUP = "Administrators"

DATE_INPUT_FORMATS = ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y')

# Application definition

INSTALLED_APPS = [
    'async_include',
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
    'djanban.apps.agility_rating',
    'djanban.apps.api',
    'djanban.apps.anonymizer',
    'djanban.apps.base',
    'djanban.apps.boards',
    'djanban.apps.charts',
    'djanban.apps.hourly_rates',
    'djanban.apps.index',
    'djanban.apps.journal',
    'djanban.apps.dev_times',
    'djanban.apps.dev_environment',
    'djanban.apps.fetch',
    'djanban.apps.forecasters',
    'djanban.apps.members',
    'djanban.apps.multiboards',
    'djanban.apps.niko_niko_calendar',
    'djanban.apps.notifications',
    'djanban.apps.password_reseter',
    'djanban.apps.reporter',
    'djanban.apps.reports',
    'djanban.apps.repositories',
    'djanban.apps.requirements',
    'djanban.apps.slideshow',
    'djanban.apps.visitors',
    'djanban.apps.workflows',
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

# Based on the tutorial that integrates Django with Angular
# (https://4sw.in/blog/2016/django-angular2-tutorial-part-2/)
ANGULAR_URL = '/ng/'
ANGULAR_URL_REGEX = r'^ng/(?P<path>.*)$'
ANGULAR_ROOT = os.path.join(BASE_DIR, 'angularapp/')

ROOT_URLCONF = 'djanban.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+"/djanban/templates"],
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
PYTZ_SERVER_TIME_ZONE = pytz.timezone(TIME_ZONE)
PYTZ_UTC_TIME_ZONE = pytz.timezone('UTC')

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
SERVER_EMAIL = settings_local.SERVER_EMAIL

# HTTPS configuration
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = False  # Django >= 1.4
USE_X_FORWARDED_PORT = False
SECURE_SSL_REDIRECT = False
SECURE_SSL_HOST = None


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
STATICFILES_DIRS = [
    BASE_DIR + "/djanban/static/"
]

TMP_DIR = BASE_DIR + "/djanban/tmp/"

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR + "/public_html/collectedstatic"

# Captcha image and font size
CAPTCHA_IMAGE_SIZE = (200, 70)
CAPTCHA_FONT_SIZE = 52

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
