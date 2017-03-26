from __future__ import unicode_literals

from django.db import models


# Notification class
from django.utils import timezone


class Notification(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    list = models.ForeignKey("boards.List", verbose_name=u"List this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    card = models.ForeignKey("boards.Card", verbose_name=u"Card this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    card_comment = models.ForeignKey("boards.CardComment", verbose_name=u"Card comment this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    sender = models.ForeignKey("members.Member", verbose_name=u"Sender of this notification", related_name="sent_notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    receiver = models.ForeignKey("members.Member", verbose_name=u"Receiver of this notification", related_name="received_notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(verbose_name=u"Notification description", default="", blank=True)
    is_read = models.BooleanField(verbose_name=u"Is this notification read?", default=False)
    reading_datetime = models.DateTimeField(verbose_name=u"When this notification was read", default=None, null=True, blank=True)
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    def read(self):
        self.reading_datetime = timezone.now()
        self.is_read = True
        self.save()

    def save(self, *args, **kwargs):
        if self.creation_datetime is None:
            self.creation_datetime = timezone.now()
        return super(Notification, self).save(*args, **kwargs)