
# Django Trello stats

Statistics and charts for Trello boards, now in a Django app.

# Requirements

Django, python-mysql and more packages specified in requirements.txt

# Local settings

Copy this code and create a settings_local.py file in your server in **src**.

Write your database credentials and your domain. Switch off debug messages.

I've used MySQL as a database but you can use whatever you want.

```python
# -*- coding: utf-8 -*-

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '<whatever string you want>'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = "<your domain>"
ALLOWED_HOSTS = [DOMAIN]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<database name>',
        'USER': '<user>',
        'PASSWORD': '<password>',
        'HOST': '',
        'PORT': ''
    }
}
```

# Sign up

First you need to sign up with the api key, token and token secret.

This action will create a new user in the system.

User your email to log in the application.

# Initialize boards and lists

Later, you need to initialize the boards.

```python
python src/manage.py init <trello_username>
```

# Fetch cards

And of course, you have to fetch the cards.

```python
python src/manage.py fetch <trello_username>
```

One good idea is set this action in a cron action and call it each day.

# Description of computed stats

- Card spent and estimated times.
- Daily spent and estimated times.
- Average time cards are in each list.
- Spent time by member by week. 

# Charts

TODO: include charts showed in application. 

# TODO
  - Workflow stats are not completed. Only the definition of workflows is fully implemented but not their stats.


# Questions? Suggestions?

Don't hesitate to contact me, write me to diegojREMOVETHISromeroREMOVETHISlopez@REMOVETHISgmail.REMOVETHIScom.

(remove REMOVETHIS to see the real email address)