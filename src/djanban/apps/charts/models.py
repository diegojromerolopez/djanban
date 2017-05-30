# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import random
from datetime import timedelta

import shortuuid
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q
from django.utils import timezone
from crequest.middleware import CrequestMiddleware


# Each one of the SVG charts of this platform
class CachedChart(models.Model):
    FORCE_UPDATE_GET_PARAM_NAME = "update"

    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    uuid = models.CharField(max_length=2048, verbose_name=u"Chart view name",
                            help_text=u"Chart view name including some optional parameters")

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="cached_charts", default=None, null=True)

    svg = models.FileField(verbose_name="SVG content of the chart")

    is_expired = models.BooleanField(verbose_name=u"Is this cache item expired?", default=False)

    # Gets a chart or False if the cached chart does not exists and must be created
    @staticmethod
    def get(board, uuid):
        # CachedChart update can be forced passing a GET parameter that would be evaluated to True
        current_request = CrequestMiddleware.get_request()
        force_update_param_value = current_request.GET.get(CachedChart.FORCE_UPDATE_GET_PARAM_NAME)
        if force_update_param_value:
            return False

        # Otherwise, try to get the CachedChart and if is old or it doesn't exist, return False
        try:
            chart = CachedChart._get(board=board, uuid=uuid)
            return chart.render_django_response()
        except CachedChart.DoesNotExist:
            return False
        except CachedChart.MultipleObjectsReturned:
            CachedChart.expire(board=board, uuid=uuid)
            return False

    @staticmethod
    def chart_life_datetime_limit(board=None):
        if board:
            return board.last_activity_datetime
        # In case there is no board, the charts are cached during 30 minutes with a random delay to avoid
        # having all charts loading at the same time
        life_of_this_cache_chart_in_seconds = 1800 + random.randint(0, 600)
        return timezone.now() - timedelta(seconds=life_of_this_cache_chart_in_seconds)

    # Get an existing CachedChart
    @staticmethod
    def _get(board, uuid):
        return CachedChart.objects.get(
            board=board, uuid=uuid, is_expired=False,
            creation_datetime__gte=CachedChart.chart_life_datetime_limit(board)
        )

    # Create a new cached chart
    @staticmethod
    def make(board, uuid, svg):
        # Select old cached chart and if it exists, update it
        life_datetime_limit = CachedChart.chart_life_datetime_limit(board)
        try:
            chart_cache = CachedChart.objects.get(
                Q(creation_datetime__lt=life_datetime_limit)|Q(is_expired=True), board=board, uuid=uuid
            )
        # There shouldn't be two charts with the same signature
        except CachedChart.MultipleObjectsReturned:
            CachedChart.objects.filter(
                Q(creation_datetime__lt=life_datetime_limit)|Q(is_expired=True), board=board, uuid=uuid
            ).delete()
            chart_cache = CachedChart(board=board, uuid=uuid)

        # If there is no old chart, create a new one
        except CachedChart.DoesNotExist:
            chart_cache = CachedChart(board=board, uuid=uuid)

        chart_cache.is_expired = False
        chart_cache.creation_datetime = timezone.now()
        chart_cache.svg.save("{0}".format(uuid, shortuuid.uuid()), ContentFile(svg))
        chart_cache.save()
        return chart_cache

    @staticmethod
    def expire(uuid, board=None):
        CachedChart.objects.filter(uuid=uuid, board=board).update(is_expired=True)

    @staticmethod
    def expire_all(board=None):
        CachedChart.objects.filter(board=board).update(is_expired=True)

    # Render a django response
    def render_django_response(self):
        from django.http import HttpResponse
        return HttpResponse(self.svg.read(), content_type='image/svg+xml')