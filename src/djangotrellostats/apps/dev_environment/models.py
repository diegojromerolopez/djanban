# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models


# An interruption of one team member
class Interruption(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Project", null=True, default=None, blank=True)
    member = models.ForeignKey("members.Member", verbose_name=u"Who suffered the interruption")

    datetime = models.DateTimeField(verbose_name=u"When did the interruption take place?")
    cause = models.TextField(verbose_name=u"Why were you interrupted?", default="", blank=True)
    comments = models.TextField(verbose_name=u"Other comments about the interruption", default="", blank=True)


# A noise measurement
class NoiseMeasurement(models.Model):
    # Based on https://www.acoustics.asn.au/conference_proceedings/AAS2011/papers/p140.pdf
    SUBJECTIVE_NOISE_LEVELS = (
        ("none", "I don't feel any noise"),
        ("library like", "A whisper is heard perfectly (library like environment)"),
        ("distracting", "The noise level is distracting and earphones or earplugs are needed"),
        ("very distracting", "Although you use earplugs or earphones, noise is slowing your work down"),
        ("noisy", "You need to shout to be heard by someone 1 meter away. Difficult to hold a conversation and to work"),
        ("very noisy", "Cannot be heard by someone 1 metre away, even when shouting. Volume level may be uncomfortable after a short time "),
    )
    member = models.ForeignKey("members.Member", verbose_name=u"Who did take the measure?")
    datetime = models.DateTimeField(verbose_name=u"When the measure was taken?")
    noise_level = models.DecimalField(verbose_name=u"Noise level in decibeles", decimal_places=4, max_digits=12)
    subjective_noise_level = models.CharField(verbose_name=u"Subjective noisel level", choices=SUBJECTIVE_NOISE_LEVELS,
                                              max_length=32, default="none")
    comments = models.TextField(verbose_name=u"Other comments about the noise in your environment",
                                default="", blank=True)


