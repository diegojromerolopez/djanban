from django.db import models


# An interruption of one team member
class Interruption(models.Model):

    class Meta:
        verbose_name = "Interruption"
        verbose_name_plural = "Interruptions"
        indexes = [models.Index(fields=("datetime", "board", "member")), models.Index(fields=("member", "datetime", "board"))]

    board = models.ForeignKey("boards.Board", on_delete=models.CASCADE, verbose_name="Project", null=True, default=None, blank=True)

    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, verbose_name="Who suffered the interruption")

    datetime = models.DateTimeField(verbose_name="When did the interruption take place?")

    interrupted_task = models.TextField(
        verbose_name="What were you doing?",
        help_text="Describe what were you doing when interrupted. "
                  "This text has the aim of helping you return to your task once the interruption has ended.",
        default="", blank=True
    )

    cause = models.TextField(verbose_name="Why were you interrupted?", default="", blank=True)

    spent_time = models.DecimalField(verbose_name="Spent time in this interruption",
                                     decimal_places=4, max_digits=12, default=None, null=True)

    comments = models.TextField(verbose_name="Other comments about the interruption", default="", blank=True)


# A noise measurement
class NoiseMeasurement(models.Model):
    # Based on https://www.acoustics.asn.au/conference_proceedings/AAS2011/papers/p140.pdf
    SUBJECTIVE_NOISE_LEVELS = (
        ("none", "I don't feel any noise"),
        ("library like", "A whisper is heard perfectly (library like environment)"),
        ("distracting", "The noise level is distracting and earphones or earplugs are needed"),
        ("very distracting", "Although you use earplugs or earphones, noise is slowing your work down"),
        ("noisy", "You need to shout to be heard by someone 1 meter away. Difficult to hold a conversation and to work"),
        ("very noisy", "Cannot be heard by someone 1 metre away, even when shouting. Volume level may be uncomfortable after a short time "),
    )
    member = models.ForeignKey("members.Member", on_delete=models.CASCADE, verbose_name="Who did take the measure?")
    datetime = models.DateTimeField(verbose_name="When the measure was taken?")
    noise_level = models.DecimalField(verbose_name="Noise level in decibeles", decimal_places=4, max_digits=12)
    subjective_noise_level = models.CharField(verbose_name="Subjective noisel level", choices=SUBJECTIVE_NOISE_LEVELS,
                                              max_length=32, default="none")
    comments = models.TextField(verbose_name="Other comments about the noise in your environment",
                                default="", blank=True)


