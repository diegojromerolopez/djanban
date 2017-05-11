# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-19 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0020_auto_20170311_0158'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='is_public',
            field=models.BooleanField(default=False, help_text='If checked, this user will be seen by other members and they will be able to add it to their boards', verbose_name='Is this member public?'),
        ),
    ]