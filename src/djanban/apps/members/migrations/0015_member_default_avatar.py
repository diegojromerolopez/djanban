# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-23 23:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0014_auto_20170211_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='default_avatar',
            field=models.ImageField(default=None, null=True, upload_to=b'', verbose_name='Default avatar'),
        ),
    ]
