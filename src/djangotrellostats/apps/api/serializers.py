# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.urls import reverse
from crequest.middleware import CrequestMiddleware

from djangotrellostats.apps.reports.models import CardReview


def serialize_board(board):
    lists_json = []
    for list_ in board.active_lists.order_by("position"):
        list_json = serialize_list(list_)

        card_list = []
        for card in list_.cards.all().order_by("position"):
            card_json = {
                "id": card.id,
                "uuid": card.uuid,
                "name": card.name,
                "description": card.description,
                "url": reverse("boards:view_card", args=(board.id, card.id,)),
                "short_url": card.short_url,
                "position": card.position,
                "is_closed": card.is_closed,
                "board": {"id": board.id, "uuid": board.uuid, "name": board.name,}
            }
            card_list.append(card_json)

        list_json["cards"] = card_list

        lists_json.append(list_json)

    board_json = {
        "id": board.id,
        "uuid": board.uuid,
        "name": board.name,
        "description": board.description,
        "local_url": reverse("boards:view", args=(board.id,)),
        "lists": lists_json,
        "members": [serialize_member(member) for member in board.members.all().order_by("initials")],
        "requirements": [serialize_requirement(requirement) for requirement in board.requirements.all()],
    }
    return board_json


# Basic card serialization
def basic_serialize_card(card):
    return {
        "id": card.id,
        "uuid": card.uuid,
        "name": card.name,
        "description": card.description,
        "local_url": reverse("boards:view_card", args=(card.board_id, card.id,)),
        "url": card.url,
        "short_url": card.short_url,
        "position": card.position,
        "is_closed": card.is_closed
    }


# Full card serialization
def serialize_card(card):
    board = card.board
    card_list = card.list

    comments_json = []
    for comment in card.comments.all().order_by("-creation_datetime"):
        comment_json = serialize_card_comment(comment, board=board)
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
        "estimated_time": card.estimated_time,
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
        "blocking_cards": [
            {
                "id": blocking_card.id,
                "uuid": blocking_card.uuid,
                "name": blocking_card.name,
                "description": blocking_card.description,
                "url": reverse("boards:view_card", args=(board.id, blocking_card.id,)),
                "short_url": blocking_card.short_url,
                "position": blocking_card.position,
                "list": {
                    "id": blocking_card.list.id,
                    "name": blocking_card.list.name,
                    "uuid": blocking_card.list.uuid,
                    "type": blocking_card.list.type,
                    "position": blocking_card.list.position
                }
            }
            for blocking_card in card.blocking_cards.order_by("creation_datetime")
            ],
        "movements": [
            {
                "id": movement.id,
                "source_list": {"id": movement.source_list.id, "name": movement.source_list.name},
                "destination_list": {"id": movement.destination_list.id, "name": movement.destination_list.name},
                "datetime": movement.datetime,
                "member": serialize_member(movement.member)
            }
            for movement in card.movements.all().order_by("-datetime")
            ],
        "reviews": [serialize_card_review(review) for review in card.reviews.all().order_by("-creation_datetime")],
        "requirements": [serialize_requirement(requirement) for requirement in card.requirements.all()],
        "charts": {
            "number_of_comments_by_member": reverse("charts:number_of_comments_by_member", args=(board.id, card.id)),
            "number_of_comments": reverse("charts:number_of_comments", args=(board.id, card.id))
        }
    }
    return card_json


# Serialize card review
def serialize_card_review(review):
    return {
        "id": review.id,
        "creation_datetime": review.creation_datetime,
        "description": review.description,
        "reviewers": [serialize_member(reviewer) for reviewer in review.reviewers.all()]
    }


# Serialize card comment
def serialize_card_comment(comment, board=None):
    if board is None:
        board = comment.board
    try:
        review = comment.review
    except CardReview.DoesNotExist:
        review = None

    author = comment.author
    comment_json = {
        "id": comment.id,
        "uuid": comment.uuid,
        "content": comment.content,
        "creation_datetime": comment.creation_datetime,
        "last_edition_datetime": comment.last_edition_datetime,
        "author": {"id": author.id, "trello_username": author.trello_username, "initials": author.initials},
        "blocking_card": {
            "id": comment.blocking_card.id,
            "uuid": comment.blocking_card.uuid,
            "name": comment.blocking_card.name,
            "description": comment.blocking_card.description,
            "url": reverse("boards:view_card", args=(board.id, comment.blocking_card.id,)),
            "short_url": comment.blocking_card.short_url,
            "position": comment.blocking_card.position,
        } if comment.blocking_card else None,
        "review": serialize_card_review(review) if review else None,
        "requirement": serialize_requirement(comment.requirement) if comment.requirement else None
    }
    return comment_json


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


# Requirement serialization
def serialize_requirement(requirement):
    return {
        "id": requirement.id,
        "code": requirement.code,
        "name": requirement.name,
        "description": requirement.description,
        "other_comments": requirement.other_comments,
        "cards": [basic_serialize_card(card) for card in requirement.cards.all()],
        "value": requirement.value,
        "estimated_number_of_hours": requirement.estimated_number_of_hours,
        "active": requirement.active,
        "spent_time": requirement.done_cards_spent_time,
        "percentage_of_completion": requirement.done_cards_percentage
    }
