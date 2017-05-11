
from __future__ import unicode_literals

from django.conf import settings
import pytz


# Localize datetime to local timezone if no timezone information is present
def localize_if_needed(unlocalized_datetime):
    tzinfo = unlocalized_datetime.tzinfo
    if tzinfo is None or unlocalized_datetime.tzinfo.utcoffset(unlocalized_datetime) is None:
        return localize(unlocalized_datetime)
    return unlocalized_datetime


# Localized unlocalized datetime
# Assumes that the datetime is unlocalized
def localize(unlocalized_datetime):
    local_timezone = pytz.timezone(settings.TIME_ZONE)
    localized_datetime = local_timezone.localize(unlocalized_datetime)
    return localized_datetime

