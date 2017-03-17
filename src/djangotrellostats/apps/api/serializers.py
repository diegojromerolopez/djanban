# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from crequest.middleware import CrequestMiddleware

from djangotrellostats.apps.boards.models import CardMemberRelationship, CardLabelRelationship, Card
from djangotrellostats.apps.reports.models import CardReview


class Serializer(object):

    def __init__(self, board=None):
        self.board = board
        self.serialized_members_by_id = None
        self.serialized_members_by_card = None
        self.current_user = None
        self.current_member = None
        self.serialized_labels_by_id = None
        self.serialized_labels_by_card = None

    def _init_member_cache(self):

        current_request = CrequestMiddleware.get_request()
        self.current_user = current_request.user
        self.current_member = None
        if hasattr(self.current_user, "member"):
            self.current_member = self.current_user.member

        if self.serialized_members_by_id is None:
            self.serialized_members_by_id = {member.id: self.serialize_member(member) for member in self.board.members.all()}
        if self.serialized_members_by_card is None:
            self.serialized_members_by_card = CardMemberRelationship.get_members_by_card(
                self.board, member_cache=self.serialized_members_by_id
            )

    def _init_label_cache(self):

        if self.serialized_labels_by_id is None:
            self.serialized_labels_by_id = {
                label.id: self.serialize_label(label) for label in self.board.labels.all()
            }

        if self.serialized_labels_by_card is None:
            self.serialized_labels_by_card = CardLabelRelationship.get_labels_by_card(
                self.board, label_cache=self.serialized_labels_by_id
            )

    def serialize_board(self):

        self._init_member_cache()
        self._init_label_cache()

        cards = self.board.cards.exclude(Q(list__type="closed")|Q(list__type="ignored")).\
            order_by("list", "position")

        cards_by_list = {list_.id: [] for list_ in self.board.active_lists.order_by("position")}
        for card in cards:
            cards_by_list[card.list_id].append(card)

        lists_json = []
        for list_ in self.board.active_lists.order_by("position"):
            list_json = self.serialize_list(list_)

            card_list = []
            for card in cards_by_list[list_.id]:
                serialized_card = self.basic_serialize_card(card=card)
                card_list.append(serialized_card)

            list_json["cards"] = card_list

            lists_json.append(list_json)

        board_json = {
            "id": self.board.id,
            "uuid": self.board.uuid,
            "name": self.board.name,
            "description": self.board.description,
            "local_url": reverse("boards:view", args=(self.board.id,)),
            "identicon_url": reverse("boards:view_identicon", args=(self.board.id, 40, 40)),
            "lists": lists_json,
            "members": [self.serialized_members_by_id[member.id] for member in self.board.members.all().order_by("id")],
            "labels": [self.serialized_labels_by_id[label.id] for label in self.board.labels.exclude(name="").order_by("name")],
            "requirements": [self.serialize_requirement(requirement) for requirement in self.board.requirements.all()],
        }
        return board_json

    # Basic card serialization
    def basic_serialize_card(self, card):
        self._init_member_cache()
        return {
            "id": card.id,
            "creation_datetime": card.creation_datetime,
            "uuid": card.uuid,
            "name": card.name,
            "description": card.description,
            "local_url": reverse("boards:view_card", args=(card.board_id, card.id,)),
            "url": card.url,
            "short_url": card.short_url,
            "position": card.position,
            "due_datetime": card.due_datetime,
            "is_closed": card.is_closed,
            "spent_time": card.spent_time,
            "estimated_time": card.estimated_time,
            "number_of_comments": card.number_of_comments,
            "number_of_forward_movements": card.number_of_forward_movements,
            "number_of_backward_movements": card.number_of_backward_movements,
            "board": {"id": self.board.id, "uuid": self.board.uuid, "name": self.board.name},
            "labels": self.serialized_labels_by_card.get(card.id, []),
            "members": self.serialized_members_by_card.get(card.id, []),
            "number_of_reviews": card.number_of_reviews
        }

    # Full card serialization
    def serialize_card(self, card):
        card_list = card.list

        comments_json = []
        for comment in card.comments.all().order_by("-creation_datetime"):
            comment_json = self.serialize_card_comment(comment)
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
            "value": card.value,
            "number_of_comments": card.number_of_comments,
            "comments": comments_json,
            "is_closed": card.is_closed,
            "creation_datetime": card.creation_datetime,
            "due_datetime": card.due_datetime,
            "spent_time": card.spent_time,
            "estimated_time": card.estimated_time,
            "lead_time": card.lead_time,
            "cycle_time": card.cycle_time,
            "labels": [self.serialize_label(label) for label in card.labels.exclude(name="").order_by("name")],
            "board": {
                "id": self.board.id,
                "uuid": self.board.uuid,
                "name": self.board.name,
                "lists": [self.serialize_list(list_) for list_ in self.board.active_lists.order_by("position")],
                "labels": [self.serialize_label(label) for label in self.board.labels.exclude(name="").order_by("name")]
            },
            "list": self.serialize_list(card_list),
            "members": [self.serialize_member(member) for member in card.members.all().order_by("id")],
            "blocking_cards": [
                {
                    "id": blocking_card.id,
                    "uuid": blocking_card.uuid,
                    "name": blocking_card.name,
                    "description": blocking_card.description,
                    "url": reverse("boards:view_card", args=(self.board.id, blocking_card.id,)),
                    "short_url": blocking_card.short_url,
                    "position": blocking_card.position,
                    "list": self.serialize_list(blocking_card.list)
                }
                for blocking_card in card.blocking_cards.order_by("creation_datetime")
                ],
            "movements": [
                {
                    "id": movement.id,
                    "source_list": self.serialize_list(movement.source_list),
                    "destination_list": self.serialize_list(movement.destination_list),
                    "datetime": movement.datetime,
                    "member": self.serialize_member(movement.member)
                }
                for movement in card.movements.all().order_by("-datetime")
                ],
            "reviews": [self.serialize_card_review(review) for review in card.reviews.all().order_by("-creation_datetime")],
            "requirements": [self.serialize_requirement(requirement) for requirement in card.requirements.all()],
            "charts": {
                "number_of_comments_by_member": reverse("charts:number_of_comments_by_member", args=(self.board.id, card.id)),
                "number_of_comments": reverse("charts:number_of_comments", args=(self.board.id, card.id))
            }
        }
        return card_json

    # Serialize label
    def serialize_label(self, label):
        return {
            "id": label.id,
            "uuid": label.uuid,
            "name": label.name,
            "color": label.color,
        }

    # Serialize card review
    def serialize_card_review(self, review):
        return {
            "id": review.id,
            "creation_datetime": review.creation_datetime,
            "description": review.description,
            "reviewers": [self.serialized_members_by_id[reviewer.id] for reviewer in review.reviewers.all()]
        }

    # Serialize card comment
    def serialize_card_comment(self, comment):
        self._init_member_cache()

        try:
            review = comment.review
        except CardReview.DoesNotExist:
            review = None

        try:
            valued_card = comment.valued_card
        except Card.DoesNotExist:
            valued_card = None

        serialized_author = self.serialized_members_by_id[comment.author_id]
        comment_json = {
            "id": comment.id,
            "uuid": comment.uuid,
            "content": comment.content,
            "creation_datetime": comment.creation_datetime,
            "last_edition_datetime": comment.last_edition_datetime,
            "author": serialized_author,
            "blocking_card": {
                "id": comment.blocking_card.id,
                "uuid": comment.blocking_card.uuid,
                "name": comment.blocking_card.name,
                "description": comment.blocking_card.description,
                "url": reverse("boards:view_card", args=(self.board.id, comment.blocking_card.id,)),
                "short_url": comment.blocking_card.short_url,
                "position": comment.blocking_card.position
            } if comment.blocking_card else None,
            "valued_card": {
                "id": valued_card.id,
                "uuid": valued_card.uuid,
                "name": valued_card.name,
                "description": valued_card.description,
                "url": reverse("boards:view_card", args=(self.board.id, valued_card.id,)),
                "short_url": valued_card.short_url,
                "position": valued_card.position
            } if valued_card else None,
            "review": self.serialize_card_review(review) if review else None,
            "requirement": self.serialize_requirement(comment.requirement) if comment.requirement else None
        }
        return comment_json

    # List serialization
    def serialize_list(self, list_):
        list_json = {
            "id": list_.id,
            "name": list_.name,
            "uuid": list_.uuid,
            "type": list_.type,
            "position": list_.position,
            "wip_limit": list_.wip_limit
        }
        return list_json

    # Member serialization
    def serialize_member(self, member):

        member_json = {
            "id": member.id,
            "external_username": member.external_username,
            "initials": member.initials,
            "is_current_user": True if self.current_member and member.id == self.current_member.id else False,
            "gravatar_url": member.gravatar_url,
            "roles_by_board": {
                member_role.board_id: member_role.type for member_role in member.roles.all()
            }
        }
        return member_json

    # Requirement serialization
    def serialize_requirement(self, requirement):
        self._init_member_cache()

        return {
            "id": requirement.id,
            "code": requirement.code,
            "name": requirement.name,
            "description": requirement.description,
            "other_comments": requirement.other_comments,
            "cards": [self.basic_serialize_card(card) for card in requirement.cards.all()],
            "value": requirement.value,
            "estimated_number_of_hours": requirement.estimated_number_of_hours,
            "active": requirement.active,
            "spent_time": requirement.done_cards_spent_time,
            "percentage_of_completion": requirement.done_cards_percentage
        }
