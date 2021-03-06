# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-05 22:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boards', '0023_auto_20160904_1643'),
        ('members', '0006_auto_20160726_1927'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interruption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='When did the interruption take place?')),
                ('cause', models.TextField(blank=True, default='', verbose_name='Why were you interrupted?')),
                ('comments', models.TextField(blank=True, default='', verbose_name='Other comments about the interruption')),
                ('board', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='boards.Board', verbose_name='Board')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.Member', verbose_name='Who suffered the interruption')),
            ],
        ),
        migrations.CreateModel(
            name='NoiseMeasurement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='When the measure was taken?')),
                ('noise_level', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Noise level in decibeles')),
                ('subjective_noise_level', models.CharField(choices=[('none', "I don't feel any noise"), ('library like', 'A whisper is heard perfectly (library like environment)'), ('distracting', 'The noise level is distracting and earphones or earplugs are needed'), ('very distracting', 'Although you use earplugs or earphones, noise is slowing your work down'), ('noisy', 'You need to shout to be heard by someone 1 meter away. Difficult to hold a conversation and to work'), ('very noisy', 'Cannot be heard by someone 1 metre away, even when shouting. Volume level may be uncomfortable after a short time ')], default='none', max_length=32, verbose_name='Subjective noisel level')),
                ('comments', models.TextField(blank=True, default='', verbose_name='Other comments about the interruption')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='members.Member', verbose_name='Who did take the measure?')),
            ],
        ),
    ]
