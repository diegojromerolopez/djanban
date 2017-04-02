# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-02 19:23
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import Sum


def set_number_of_mentioned_members(apps, schema):
    Card = apps.get_model("boards", "Card")
    CardComment = apps.get_model("boards", "CardComment")
    cards = Card.objects.all()
    for card in cards:
        card.number_of_mentioned_members = CardComment.objects.filter(card=card).\
            aggregate(num_mentions=Sum("number_of_mentioned_members")).get("num_mentions", 0)
        if card.number_of_mentioned_members is None:
            card.number_of_mentioned_members = 0
        card.save()


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0063_auto_20170402_2053'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='number_of_mentioned_members',
            field=models.PositiveIntegerField(default=0, verbose_name='Number of mentioned members in the comments of this card'),
        ),
        migrations.RunPython(set_number_of_mentioned_members)
    ]
