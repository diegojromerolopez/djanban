import re

from django.db import models

# Notification class
from django.db.models import Q
from django.utils import timezone


class Notification(models.Model):
    board = models.ForeignKey(
        "boards.Board",
        verbose_name="Board this notification belongs to",
        related_name="notifications",
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
    )
    list = models.ForeignKey(
        "boards.List",
        verbose_name="List this notification belongs to",
        related_name="notifications",
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
    )
    card = models.ForeignKey(
        "boards.Card",
        verbose_name="Card this notification belongs to",
        related_name="notifications",
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
    )
    card_comment = models.ForeignKey(
        "boards.CardComment",
        verbose_name="Card comment this notification belongs to",
        related_name="notifications",
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
    )
    sender = models.ForeignKey(
        "members.Member",
        verbose_name="Sender of this notification",
        related_name="sent_notifications",
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
    )
    receiver = models.ForeignKey(
        "members.Member",
        verbose_name="Receiver of this notification",
        related_name="received_notifications",
        null=True,
        default=None,
        blank=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField(
        verbose_name="Notification description", default="", blank=True
    )
    is_read = models.BooleanField(
        verbose_name="Is this notification read?", default=False
    )
    reading_datetime = models.DateTimeField(
        verbose_name="When this notification was read",
        default=None,
        null=True,
        blank=True,
    )
    creation_datetime = models.DateTimeField(verbose_name="Creation datetime")

    def read(self):
        self.reading_datetime = timezone.now()
        self.is_read = True
        self.save()

    def save(self, *args, **kwargs):
        if self.creation_datetime is None:
            self.creation_datetime = timezone.now()
        return super().save(*args, **kwargs)

    # Add new card comment notifications
    @staticmethod
    def add_card_comment(card_comment, card):
        board = card.board
        card_comment_content = card_comment.content
        # Adding blocking card
        if (
            card_comment.blocking_card
            and card_comment.blocking_card.list.type != "done"
        ):
            for member in card.members.all():
                Notification(
                    board=board,
                    card=card,
                    card_comment=card_comment,
                    sender=card_comment.author,
                    receiver=member,
                    description="{0}: card {0} is blocked by {1}".format(
                        board.name, card.name, ),
                ).save()

        # Adding reviews
        if card_comment.review:
            for member in card.members.all():
                Notification(
                    board=board,
                    card=card,
                    card_comment=card_comment,
                    sender=card_comment.author,
                    receiver=member,
                    description=f"{board.name}: review of card {card.name} by {card_comment.author}",
                ).save()

        # Adding mentions
        mentions = re.findall(r"@[\w\d]+", card_comment_content)
        usernames = [
            mention.replace("@", "") for mention in mentions if mention != "@board"
        ]
        members = board.members.filter(
            Q(user__username__in=usernames)
            | Q(trello_member_profile__username__in=usernames)
        )
        for member in members:
            Notification(
                board=board,
                card=card,
                card_comment=card_comment,
                sender=card_comment.author,
                receiver=member,
                description=f"{board.name}: Mention of {member.external_username} in comment {card.name}",
            ).save()

    # Add card movement notifications
    @staticmethod
    def move_card(mover, card, board=None):
        if board is None:
            board = card.board

        # Notify a movement to the members of this card
        for member in card.members.all():
            Notification(
                board=board,
                card=card,
                sender=mover,
                receiver=member,
                description=f"{board.name}: card {card.name} moved to {card.list.name}",
            ).save()

        # Unblocking
        blocked_cards = card.blocked_cards.all()
        if blocked_cards.exists():
            for blocked_card in blocked_cards:
                # Send the notification to all card members
                for member in card.members.all():
                    Notification(
                        board=board,
                        card=card,
                        sender=mover,
                        receiver=member,
                        description=f"{board.name}: card {blocked_card.name} is no longer blocked by {card.name}",
                    ).save()
                    # If card is no longer blocked by any card, it can be moved. It is free.
                    if not blocked_card.blocking_cards.exclude(
                        list__type="done"
                    ).exists():
                        Notification(
                            board=board,
                            card=card,
                            sender=mover,
                            receiver=member,
                            description=f"{board.name}: card {blocked_card.name} can be started",
                        ).save()
