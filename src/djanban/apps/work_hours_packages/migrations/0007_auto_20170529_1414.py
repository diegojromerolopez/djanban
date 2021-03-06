# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-29 12:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_hours_packages', '0006_auto_20170529_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workhourspackage',
            name='number_of_hours',
            field=models.DecimalField(decimal_places=2, help_text='Number of hours of this package.', max_digits=10, verbose_name='Number of hours'),
        ),
        migrations.AlterField(
            model_name='workhourspackage',
            name='offset_hours',
            field=models.IntegerField(blank=True, default=0, help_text='This hours will be added as an initial offset of the spent time measurements gotten in the date interval', verbose_name='Offset hours'),
        ),
    ]
