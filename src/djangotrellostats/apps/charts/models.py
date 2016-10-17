# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shortuuid
from datetime import timedelta
from django.conf import settings

from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models

from django.utils import timezone
import os
from io import open


class CachedChart(models.Model):

    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    uuid = models.CharField(max_length=1024, verbose_name=u"Chart view name",
                            help_text=u"Chart view name including some optional parameters")

    board = models.ForeignKey("boards.Board", verbose_name=u"Board", related_name="chart_caches", default=None, null=True)

    svg = models.FileField(verbose_name="SVG content of the chart")

    # Get an existing CachedChart
    @staticmethod
    def get(board, uuid):
        if board:
            return CachedChart.objects.get(board=board, uuid=uuid, creation_datetime__gte=board.last_fetch_datetime)

        # In case there is no board, the charts are cached during 30 minutes
        return CachedChart.objects.get(board=None, uuid=uuid, creation_datetime__gte=timezone.now() - timedelta(minutes=30))

    # Create a new cached chart
    @staticmethod
    def make(board, uuid, svg):
        chart_cache = CachedChart(board=board, uuid=uuid, creation_datetime=timezone.now())
        chart_cache.svg.save("{0}".format(uuid, shortuuid.uuid()), ContentFile(svg))
        chart_cache.save()
        return chart_cache

    # Render a django response
    def render_django_response(self):
        from django.http import HttpResponse
        return HttpResponse(self.svg.read(), content_type='image/svg+xml')