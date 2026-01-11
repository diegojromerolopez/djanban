# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import
from djanban.apps.boards.models import Label


# Label updater
class LabelUpdater(object):

    # Creates a label if there is some change between Trello's label and this one
    @staticmethod
    def update(trello_label, board):
        try:
            label = Label.objects.get(board=board, uuid=trello_label.id)
            # If a update of the label is needed (in case of name or color change), update both attributes
            if label.name != trello_label.name or label.color != trello_label.color:
                label.name = trello_label.name
                label.color = trello_label.color
                label.save()
        # If the label does not exist, create it with the trello label values
        except Label.DoesNotExist:
            label = Label(board=board, uuid=trello_label.id, name=trello_label.name, color=trello_label.color)
            label.save()
        return label
