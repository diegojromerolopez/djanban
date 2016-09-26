# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pygal
from django.core.exceptions import ObjectDoesNotExist


# Show the agility rating for a project
def view(board):
    radar_chart = pygal.Radar(fill=True)
    radar_chart.title = 'Agility rating for project {0}'.format(board.name)
    radar_chart.x_labels = ['Personnel', 'Dynamism', 'Culture', 'Size', 'Criticality']

    try:
        agility_rating = board.agility_rating
        radar_chart.add(
            board.name,
            [
                int(agility_rating.personnel), int(agility_rating.dynamism), int(agility_rating.culture),
                int(agility_rating.size), int(agility_rating.criticality)
            ]
        )
    except ObjectDoesNotExist:
        pass

    return radar_chart.render_django_response()
