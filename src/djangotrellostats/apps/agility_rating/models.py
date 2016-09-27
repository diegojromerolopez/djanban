# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


# Agility rating according to Boehm & Turner (extracted from their book "Balancing Agility & Discipline")
class ProjectAgilityRating(models.Model):
    class Meta:
        verbose_name = u"project agility rating"
        verbose_name_plural = u"project agility ratings"

    PERSONNEL_CHOICES = (
        ("1", "0% Level 1B / 35% Level 2 and 3"),
        ("2", "10% Level 1B / 30% Level 2 and 3"),
        ("3", "20% Level 1B / 25% Level 2 and 3"),
        ("4", "30% Level 1B / 20% Level 2 and 3"),
        ("5", "40% Level 1B / 15% Level 2 and 3")
    )

    DYNAMISM_CHOICES = (
        ("1", "50%"),
        ("2", "30%"),
        ("3", "10%"),
        ("4", "5%"),
        ("5", "1%"),
    )

    CULTURE_CHOICES = (
        ("1", "90%"),
        ("2", "70%"),
        ("3", "50%"),
        ("4", "30%"),
        ("5", "10%")
    )

    SIZE_CHOICES = (
        ("1", "3"),
        ("2", "10"),
        ("3", "30"),
        ("4", "100"),
        ("5", "300")
    )

    CRITICALITY_CHOICES = (
        ("1", "Comfort"),
        ("2", "Discretionary funds"),
        ("3", "Essential funds"),
        ("4", "Single life"),
        ("5", "Many lives"),
    )

    # Project rated
    board = models.OneToOneField("boards.Board", verbose_name=u"Project", related_name="agility_rating")

    # Personnel dimension
    personnel = models.CharField(verbose_name="Personnel", max_length=64, choices=PERSONNEL_CHOICES,
                                 help_text=u"Personnel dimension in extended Cockburn scale.")

    # Dynamism dimension
    dynamism = models.CharField(verbose_name="Dynamism", max_length=64, choices=DYNAMISM_CHOICES,
                                help_text=u"Percentage of requirement changes per month.")

    # Culture
    culture = models.CharField(
        verbose_name="Culture", max_length=64, choices=CULTURE_CHOICES,
        help_text=u"Thriving on chaos vs. order. What percentage of tasks are disciplined done vs. on a chaotic way."
    )

    # Size (number of workers)
    size = models.CharField(verbose_name="Size", max_length=64, choices=SIZE_CHOICES,
                            help_text=u"Number of personnel.")

    # Criticality (consequences of a software defect)
    criticality = models.CharField(verbose_name="Criticality", max_length=64, choices=CRITICALITY_CHOICES,
                                   help_text=u"Consequences of a software defect.")

    @property
    def value(self):
        value = (int(self.personnel) + int(self.dynamism) + int(self.culture) + int(self.size) + int(self.criticality)) / 5.0
        return 50.0 - value
