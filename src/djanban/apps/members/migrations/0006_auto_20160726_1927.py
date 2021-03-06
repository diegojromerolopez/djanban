# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 17:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0005_auto_20160724_2331'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='real_working_hours_per_week',
        ),
        migrations.AddField(
            model_name='member',
            name='minimum_working_hours_per_day',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Minimum number hours this developer should complete each day'),
        ),
        migrations.AddField(
            model_name='member',
            name='minimum_working_hours_per_week',
            field=models.PositiveIntegerField(blank=True, default=None, null=True, verbose_name='Minimum number of hours this developer should complete per week'),
        ),
        migrations.AlterField(
            model_name='member',
            name='is_developer',
            field=models.BooleanField(default=False, help_text='Informs if this member is a developer and hence will receive reports and other information', verbose_name='Is this member a developer?'),
        ),
        migrations.AlterField(
            model_name='member',
            name='on_holidays',
            field=models.BooleanField(default=False, help_text='If the developer is on holidays will stop receiving reports and other emails', verbose_name='Is this developer on holidays?'),
        ),
    ]
