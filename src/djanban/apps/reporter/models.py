from django.db import models


# Motivational video
class MotivationalVideo(models.Model):
    url = models.URLField(verbose_name="URL for this video")
    uses = models.PositiveIntegerField(verbose_name="Number of times this video has been included in emails",
                                       default=0)
