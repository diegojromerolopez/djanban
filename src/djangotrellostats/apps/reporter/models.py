from __future__ import unicode_literals

import re
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db import models
from django.db.models import Avg, Sum
from django.db.models.query_utils import Q
from django.utils import timezone
import requests
import threading
import numpy
import datetime
import time
import math
import pytz
from isoweek import Week

from trello import Board as TrelloBoard, ResourceUnavailable
from collections import namedtuple
from djangotrellostats.apps.dev_times.models import DailySpentTime


# Motivational video
class MotivationalVideo(models.Model):
    url = models.URLField(verbose_name=u"URL for this video")
    uses = models.PositiveIntegerField(verbose_name=u"Number of times this video has been included in emails",
                                       default=0)
