from __future__ import unicode_literals

from django.db import models


# Motivational video
class MotivationalVideo(models.Model):
    url = models.URLField(verbose_name=u"URL for this video")
    uses = models.PositiveIntegerField(verbose_name=u"Number of times this video has been included in emails",
                                       default=0)
