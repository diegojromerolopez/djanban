# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-28 19:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dev_times', '0002_dailyspenttime_rate_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyspenttime',
            name='description',
            field=models.TextField(default='', verbose_name='Description of the task'),
            preserve_default=False,
        ),
    ]