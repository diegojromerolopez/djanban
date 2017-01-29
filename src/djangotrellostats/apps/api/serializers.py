# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.urls import reverse
from crequest.middleware import CrequestMiddleware


# Card serialization
def serialize_card(card):
    board = card.board
    card_list = card.list

    comments_json = []
    for comment in card.comments.all().order_by("-creation_datetime"):
        author = comment.author
        comment_json = {
            "id": comment.id,
            "uuid": comment.uuid,
            "content": comment.content,
            "creation_datetime": comment.creation_datetime,
            "last_edition_datetime": comment.last_edition_datetime,
            "author": {"id": author.id, "trello_username": author.trello_username, "initials": author.initials}
        }
        comments_json.append(comment_json)

    card_json = {
        "id": card.id,
        "uuid": card.uuid,
        "name": card.name,
        "description": card.description,
        "local_url": reverse("boards:view_card", args=(card.board_id, card.id,)),
        "url": card.url,
        "short_url": card.short_url,
        "position": card.position,
        "comments": comments_json,
        "is_closed": card.is_closed,
        "creation_datetime": card.creation_datetime,
        "due_datetime": card.due_datetime,
        "spent_time": card.spent_time,
        "lead_time": card.lead_time,
        "cycle_time": card.cycle_time,
        "labels": [
            {"id": label.id, "uuid": label.uuid, "name": label.name, "color": label.color}
            for label in card.labels.exclude(name="").order_by("name")
        ],
        "board": {
            "id": board.id,
            "uuid": board.uuid,
            "name": board.name,
            "lists": [
                {
                    "id": list_.id,
                    "name": list_.name,
                    "uuid": list_.uuid,
                    "type": list_.type,
                    "position": list_.position
                }
                for list_ in board.active_lists.order_by("position")
                ],
            "labels": [
                {"id": label.id, "uuid": label.uuid, "name": label.name, "color": label.color}
                for label in board.labels.exclude(name="").order_by("name")
            ]
        },
        "list": serialize_list(card_list),
        "members": [serialize_member(member) for member in card.members.all().order_by("initials")],
        "pending_blocking_cards": [
            {
                "id": pending_blocking.id,
                "uuid": pending_blocking.uuid,
                "name": pending_blocking.name,
                "description": pending_blocking.description,
                "url": reverse("boards:view_card", args=(board.id, pending_blocking.id,)),
                "short_url": pending_blocking.short_url,
                "position": pending_blocking.position
            }
            for pending_blocking in card.pending_blocking_cards.order_by("creation_datetime")
            ],
        "movements": [
            {
                "id": movement.id,
                "source_list": {"id": movement.source_list.id, "name": movement.source_list.name},
                "destination_list": {"id": movement.destination_list.id, "name": movement.destination_list.name},
                "datetime": movement.datetime,
                "member": serialize_member(movement.member)
            }
            for movement in card.movements.all().order_by("datetime")
            ],
        "charts": {
            "number_of_comments_by_member": reverse("charts:number_of_comments_by_member", args=(board.id, card.id)),
            "number_of_comments": reverse("charts:number_of_comments", args=(board.id, card.id))
        }
    }
    return card_json


# List serialization
def serialize_list(list_):
    list_json = {
        "id": list_.id,
        "name": list_.name,
        "uuid": list_.uuid,
        "type": list_.type,
        "position": list_.position
    }
    return list_json


# Member serialization
def serialize_member(member):
    current_request = CrequestMiddleware.get_request()
    current_user = current_request.user
    current_member = None
    if hasattr(current_user, "member"):
        current_member = current_user.member

    member_json = {
        "id": member.id,
        "trello_username": member.trello_username,
        "extern_username": member.extern_username,
        "initials": member.initials,
        "is_current_user": True if current_member and member.id == current_member.id else False
    }
    return member_json