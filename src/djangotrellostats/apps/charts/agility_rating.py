# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pygal
from django.core.exceptions import ObjectDoesNotExist


# Show the agility rating for a project
def view(board):
    radar_chart = pygal.Radar(show_x_labels=True, show_y_labels=True, fill=True)
    radar_chart.title = 'Agility rating for project {0}'.format(board.name)
    radar_chart.x_labels = ['Personnel', 'Criticality', 'Culture', 'Size', 'Dynamism']

    radar_chart.add("Plan-Driven", [5, 5, 5, 5, 5])
    radar_chart.add("Agile", [1, 1, 1, 1, 1])
    try:
        agility_rating = board.agility_rating
        radar_chart.add(
            board.name,
            [
                int(agility_rating.personnel), int(agility_rating.criticality), int(agility_rating.culture),
                int(agility_rating.size), int(agility_rating.dynamism)
            ]
        )
    except ObjectDoesNotExist:
        pass

    return radar_chart.render_django_response()
