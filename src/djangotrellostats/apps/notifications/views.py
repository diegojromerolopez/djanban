# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from djangotrellostats.apps.base.decorators import member_required
from djangotrellostats.apps.notifications.models import Notification


# Mark notifications as read
@member_required
def mark_as_read(request):
    if request.method != "POST":
        raise Http404

    oldest_notification_id = request.POST.get("oldest_notification")
    if Notification.objects.filter(id=oldest_notification_id).exists():
        unread_notifications = Notification.objects.filter(id__gte=oldest_notification_id, is_read=False)
        number_of_notifications = unread_notifications.count()
        unread_notifications.update(is_read=True, reading_datetime=timezone.now())
        return JsonResponse({"message": "{0} notifications have been read".format(number_of_notifications)})

    return JsonResponse({"message": "No unread notifications"}, status=404)
