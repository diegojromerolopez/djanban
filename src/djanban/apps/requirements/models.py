from django.db import models
from django.db.models import Sum


# A requirement for a project
class Requirement(models.Model):
    board = models.ForeignKey(
        "boards.Board",
        on_delete=models.CASCADE,
        verbose_name="Board",
        related_name="requirements",
    )

    code = models.CharField(
        max_length=16, verbose_name="Unique code of this requirement", unique=True
    )

    name = models.CharField(max_length=256, verbose_name="Name of this requirement")

    description = models.TextField(
        verbose_name="Description of this requirement",
        help_text="Long description of this requirement describing behavior or "
        "pointing to other resources.",
    )

    other_comments = models.TextField(
        verbose_name="Comments",
        default="",
        blank=True,
        help_text="Private comments for the PM and the developers",
    )

    cards = models.ManyToManyField(
        "boards.Card",
        verbose_name="Tasks that depend on this requirement",
        related_name="requirements",
    )

    value = models.PositiveIntegerField(
        verbose_name="Value of this requirement", default=0
    )

    estimated_number_of_hours = models.PositiveIntegerField(
        verbose_name="Estimated number of hours to be completed",
        help_text="Cost in hours to complete this requirement.",
        blank=True,
        default=None,
        null=True,
    )

    active = models.BooleanField(
        verbose_name="Is this requirement active?",
        help_text="Is this requirement is not active it will treat  as a wish of the client "
        "but not as a real requirement",
        default=True,
    )

    # Alias of card_comments attribute
    @property
    def comments(self):
        return self.card_comments

    @property
    def done_cards(self):
        return self.cards.filter(list__type="done")

    @property
    def done_cards_percentage(self):
        num_cards = self.cards.all().count()
        if num_cards == 0:
            return 0
        return self.done_cards.count() * 100.0 / num_cards

    @property
    def done_cards_spent_time(self):
        done_cards_spent_time = self.done_cards.aggregate(sum=Sum("spent_time"))["sum"]
        if done_cards_spent_time is None:
            return 0
        return done_cards_spent_time

    @property
    def pending_cards(self):
        return self.cards.exclude(list__type="done")
