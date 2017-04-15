# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from decimal import Decimal
from djangotrellostats.apps.boards.models import List


# Card serializer used in the DataFrame creation
class CardSerializer(object):

    def __init__(self, card, members):
        self.card = card
        self.members = members

    def serialize(self):
        card = self.card
        card_age_in_seconds_decimal = Decimal(card.age_in_board.seconds / 3600.0).quantize(Decimal("1.000"))
        card_age_in_seconds = float(card_age_in_seconds_decimal)
        num_forward_movements = 0
        if card_age_in_seconds > 0:
            if card.number_of_forward_movements > 0:
                num_forward_movements = float(
                    (card.number_of_forward_movements / card_age_in_seconds_decimal).quantize(Decimal("1.000")))
            num_backward_movements = 0
            if card.number_of_backward_movements > 0:
                num_backward_movements = float(
                    (card.number_of_backward_movements / card_age_in_seconds_decimal).quantize(Decimal("1.000")))
        else:
            num_forward_movements = 0
            num_backward_movements = 0
        name_num_words = len(re.split(r"\s+", card.name))
        description_num_words = len(re.split(r"\s+", card.description))
        card_data = {
            "card_spent_time": float(card.spent_time) if card.spent_time else 0,
            "num_time_measurements": card.daily_spent_times.count(),
            "card_age": card_age_in_seconds,
            "num_forward_movements": num_forward_movements,
            "num_backward_movements": num_backward_movements,
            "num_comments": float(card.number_of_comments),
            "num_blocking_cards": card.blocking_cards.count(),
            "card_value": float(card.value) if card.value else 0,
            "name_length": len(card.name),
            "name_num_words": name_num_words,
            "description_length": len(card.description),
            "description_num_words": description_num_words,
            "num_mentioned_members": card.number_of_mentioned_members,
            "num_members": card.members.count(),
            "num_labels": card.labels.count(),
            "has_red_label": 1 if card.labels.filter(color="red") else 0,
            "has_orange_label": 1 if card.labels.filter(color="orange") else 0,
            "has_yellow_label": 1 if card.labels.filter(color="yellow") else 0
        }

        # Member that work in this card
        for card_member in card.members.all():
            card_data[card_member.external_username] = 1
        for member in self.members:
            if member.external_username not in card_data:
                card_data[member.external_username] = 0

        # Creation list type
        for list_type in List.ACTIVE_LIST_TYPES:
            card_data["creation_list_type_{0}".format(list_type)] = 0

        creation_list = card.creation_list
        if creation_list:
            card_data["creation_list_type_{0}".format(creation_list.type)] = 1

        # Time per list type
        time_per_list_type = card.time_in_each_list_type
        for list_type in List.ACTIVE_LIST_TYPES:
            if list_type in time_per_list_type:
                card_data["time_in_list_type_{0}".format(list_type)] = time_per_list_type[list_type]
            else:
                card_data["time_in_list_type_{0}".format(list_type)] = 0

        return card_data
