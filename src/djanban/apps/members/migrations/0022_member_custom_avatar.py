# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-19 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0021_auto_20170319_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='custom_avatar',
            field=models.ImageField(default=None, null=True, upload_to=b'', verbose_name='Custom avatar'),
        ),
    ]
