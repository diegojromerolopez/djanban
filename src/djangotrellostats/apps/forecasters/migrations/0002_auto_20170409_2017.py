# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-09 18:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forecasters', '0001_initial'),
    ]

    operations = [
        migrations.RenameField("Forecaster", "creator", "last_updater")
    ]