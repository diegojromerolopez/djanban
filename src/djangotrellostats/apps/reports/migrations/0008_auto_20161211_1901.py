# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-12-11 18:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0009_member_max_number_of_boards'),
        ('boards', '0040_auto_20161112_1350'),
        ('reports', '0007_cardmovement_member'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_datetime', models.DateTimeField(verbose_name='Date and time this card has been reviewed')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_reviews', to='boards.Board', verbose_name='Board')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='boards.Card', verbose_name='Card')),
                ('reviewers', models.ManyToManyField(related_name='card_reviews', to='members.Member', verbose_name='Members')),
            ],
        ),
        migrations.AlterField(
            model_name='cardmovement',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movements', to='boards.Card', verbose_name='Card'),
        ),
    ]