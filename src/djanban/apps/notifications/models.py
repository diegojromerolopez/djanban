from __future__ import unicode_literals

import re

from django.db import models


# Notification class
from django.db.models import Q
from django.utils import timezone


class Notification(models.Model):
    board = models.ForeignKey("boards.Board", verbose_name=u"Board this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    list = models.ForeignKey("boards.List", verbose_name=u"List this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    card = models.ForeignKey("boards.Card", verbose_name=u"Card this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    card_comment = models.ForeignKey("boards.CardComment", verbose_name=u"Card comment this notification belongs to", related_name="notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    sender = models.ForeignKey("members.Member", verbose_name=u"Sender of this notification", related_name="sent_notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    receiver = models.ForeignKey("members.Member", verbose_name=u"Receiver of this notification", related_name="received_notifications", null=True, default=None, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(verbose_name=u"Notification description", default="", blank=True)
    is_read = models.BooleanField(verbose_name=u"Is this notification read?", default=False)
    reading_datetime = models.DateTimeField(verbose_name=u"When this notification was read", default=None, null=True, blank=True)
    creation_datetime = models.DateTimeField(verbose_name=u"Creation datetime")

    def read(self):
        self.reading_datetime = timezone.now()
        self.is_read = True
        self.save()

    def save(self, *args, **kwargs):
        if self.creation_datetime is None:
            self.creation_datetime = timezone.now()
        return super(Notification, self).save(*args, **kwargs)

    # Add new card comment notifications
    @staticmethod
    def add_card_comment(card_comment, card):
        board = card.board
        card_comment_content = card_comment.content
        # Adding blocking card
        if card_comment.blocking_card and card_comment.blocking_card.list.type != "done":
            for member in card.members.all():
                Notification(
                    board=board, card=card, card_comment=card_comment,
                    sender=card_comment.author, receiver=member,
                    description="{0}: card {0} is blocked by {1}".format(board.name, card.name, card_comment.blocking_card.name)
                ).save()

        # Adding reviews
        if card_comment.review:
            for member in card.members.all():
                Notification(
                    board=board, card=card, card_comment=card_comment,
                    sender=card_comment.author, receiver=member,
                    description="{0}: review of card {1} by {2}".format(board.name, card.name, card_comment.author)
                ).save()

        # Adding mentions
        mentions = re.findall(r"@[\w\d]+", card_comment_content)
        usernames = [mention.replace("@", "") for mention in mentions if mention != "@board"]
        members = board.members.filter(Q(user__username__in=usernames)|Q(trello_member_profile__username__in=usernames))
        for member in members:
            Notification(
                board=board, card=card, card_comment=card_comment,
                sender=card_comment.author, receiver=member,
                description="{0}: Mention of {1} in comment {2}".format(board.name, member.external_username, card.name)
            ).save()

    # Add card movement notifications
    @staticmethod
    def move_card(mover, card, board=None):
        if board is None:
            board = card.board

        # Notify a movement to the members of this card
        for member in card.members.all():
            Notification(
                board=board, card=card,
                sender=mover, receiver=member,
                description="{0}: card {1} moved to {2}".format(board.name, card.name, card.list.name)
            ).save()

        # Unblocking
        blocked_cards = card.blocked_cards.all()
        if blocked_cards.exists():
            for blocked_card in blocked_cards:
                # Send the notification to all card members
                for member in card.members.all():
                    Notification(
                        board=board, card=card,
                        sender=mover, receiver=member,
                        description="{0}: card {1} is no longer blocked by {2}".format(board.name, blocked_card.name, card.name)
                    ).save()
                    # If card is no longer blocked by any card, it can be moved. It is free.
                    if not blocked_card.blocking_cards.exclude(list__type="done").exists():
                        Notification(
                            board=board, card=card,
                            sender=mover, receiver=member,
                            description="{0}: card {1} can be started".format(board.name, blocked_card.name)
                        ).save()