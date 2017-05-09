# -*- coding: utf-8 -*-

from random import randint
from django import template
from djanban.apps.reporter.models import MotivationalVideo
from django.template.loader import get_template

register = template.Library()


@register.simple_tag
def random_motivational_video():
    motivational_videos = MotivationalVideo.objects.all()
    if motivational_videos.exists():
        random_video = motivational_videos[randint(0, motivational_videos.count() - 1)]
        replacements = {"motivational_video": random_video}
        return get_template('reporter/motivation_tags/motivational_video.html').render(replacements)
    return None
