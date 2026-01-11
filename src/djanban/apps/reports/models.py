from django.db import models


# Movements the cards suffer
class CardMovement(models.Model):

    class Meta:
        verbose_name = "Card movement"
        verbose_name_plural = "Card movements"
        indexes = [models.Index(fields=("board", "card", "source_list", "datetime", "destination_list")), models.Index(fields=("board", "card", "destination_list", "datetime", "source_list")), models.Index(fields=("board", "destination_list", "datetime", "source_list")), models.Index(fields=("board", "card", "datetime")), models.Index(fields=("board", "type", "source_list", "destination_list")), models.Index(fields=("board", "destination_list", "datetime"))]

    CARD_MOVEMENT_TYPES = (
        ("forward", "Forward"),
        ("backward", "Backward"),
    )

    board = models.ForeignKey("boards.Board", on_delete=models.CASCADE, verbose_name="Board", related_name="card_movements")

    card = models.ForeignKey("boards.Card", on_delete=models.CASCADE, verbose_name="Card", related_name="movements")

    type = models.CharField(verbose_name="Movement type", choices=CARD_MOVEMENT_TYPES, max_length=32)

    source_list = models.ForeignKey("boards.List", on_delete=models.CASCADE, verbose_name="Source list",
                                    related_name="source_movements", null=True)

    destination_list = models.ForeignKey("boards.List", on_delete=models.CASCADE, verbose_name="Destination list",
                                         related_name="destination_movements")

    datetime = models.DateTimeField(verbose_name="Date and time this card has been moved")

    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, verbose_name="Member", related_name="card_movements",
                               null=True, default=None)

    def __str__(self):
        return f"{self.source_list.name} -> {self.destination_list.name} (on {self.datetime})"


# Reviews of a card
class CardReview(models.Model):
    board = models.ForeignKey("boards.Board", on_delete=models.CASCADE, verbose_name="Board", related_name="card_reviews")
    card = models.ForeignKey("boards.Card", on_delete=models.CASCADE, verbose_name="Card", related_name="reviews")
    description = models.TextField(verbose_name="Description of the review", default="", blank=True)
    reviewers = models.ManyToManyField("members.Member", verbose_name="Members", related_name="card_reviews")
    creation_datetime = models.DateTimeField(verbose_name="Date and time this card has been reviewed")

    @staticmethod
    def create(card_comment, reviewers, description=""):
        # Create the card review
        card = card_comment.card
        board = card.board
        card_review = CardReview(
            card=card, board=board, description=description,
            creation_datetime=card_comment.creation_datetime
        )
        card_review.save()

        # Assign the reviewers
        for reviewer in reviewers:
            card_review.reviewers.add(reviewer)
        return card_review

    @staticmethod
    def update(card_comment, reviewers, description=""):

        # Get the card review
        card_review = card_comment.review
        card_review.reviewers.clear()

        # Update the reviewers
        for reviewer in reviewers:
            card_review.reviewers.add(reviewer)

        # Update the description
        card_review.description = description
        card_review.save()
        return card_review

    @staticmethod
    def update_or_create(card_comment, reviewers, description=""):
        try:
            return CardReview.update(card_comment, reviewers, description)
        except CardReview.DoesNotExist:
            return CardReview.create(card_comment, reviewers, description)


# Recipient of periodic reports
class ReportRecipient(models.Model):
    first_name = models.CharField(verbose_name="Name of this recipient", blank=True, default="", max_length=128)
    last_name = models.CharField(verbose_name="Last name of this recipient", blank=True, default="", max_length=128)
    email = models.EmailField(verbose_name="Email of the recipient", unique=True)
    boards = models.ManyToManyField("boards.Board", verbose_name="Boards", related_name="report_recipients")
    is_active = models.BooleanField(
        verbose_name="Is active?", help_text="Only active report recipients will be notified", default=True, blank=True
    )
    send_errors = models.BooleanField(
        verbose_name="Send platform errors?",
        help_text="Only report recipients with this option enabled will receive 500 error notifications",
        default=False, blank=True
    )

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email