from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

SCORE_VALIDATORS = [MinValueValidator(1), MaxValueValidator(10)]

class Player(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Verfügbar"
        INJURED = "injured", "Verletzt"
        RECOVERY = "recovery", "Aufbau"
        ABSENT = "absent", "Abwesend"

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    shirt_number = models.PositiveSmallIntegerField(unique=True)
    position = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["shirt_number"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()

    def __str__(self):
        return f"#{self.shirt_number} {self.full_name}"

class TeamEvent(models.Model):
    class EventType(models.TextChoices):
        TRAINING = "training", "Training"
        MATCH = "match", "Spiel"
        RECOVERY = "recovery", "Regeneration"
        MEETING = "meeting", "Besprechung"
        OTHER = "other", "Sonstiges"

    title = models.CharField(max_length=160)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.TRAINING)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return self.title

class TrainingSession(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Geplant"
        COMPLETED = "completed", "Abgeschlossen"
        CANCELLED = "cancelled", "Abgesagt"

    title = models.CharField(max_length=160, default="Teamtraining")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=160, blank=True)
    focus = models.CharField(max_length=220, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-starts_at"]

    def __str__(self):
        return f"{self.title} – {self.starts_at:%d.%m.%Y}"

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Dabei"
        CANCELLED = "cancelled", "Abgesagt"
        INJURED = "injured", "Verletzt"
        LATE = "late", "Verspätet"

    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name="attendance")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="attendance")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    comment = models.CharField(max_length=220, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["training", "player"], name="unique_training_player")]

class TaskAssignment(models.Model):
    training = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name="tasks")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="tasks")
    task = models.CharField(max_length=220)
    completed = models.BooleanField(default=False)

class PlayerEvaluation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="evaluations")
    evaluated_at = models.DateTimeField(auto_now_add=True)
    mentality = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    physicality = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    performance = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    potential = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS, default=7)
    comment = models.TextField(blank=True)
    coach = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-evaluated_at"]

    @property
    def average(self):
        return round((self.mentality + self.physicality + self.performance) / 3, 1)

class Match(models.Model):
    class Venue(models.TextChoices):
        HOME = "home", "Heim"
        AWAY = "away", "Auswärts"
        NEUTRAL = "neutral", "Neutral"

    opponent = models.CharField(max_length=160)
    kickoff = models.DateTimeField()
    competition = models.CharField(max_length=160, blank=True)
    location = models.CharField(max_length=160, blank=True)
    venue = models.CharField(max_length=20, choices=Venue.choices, default=Venue.HOME)
    goals_for = models.PositiveSmallIntegerField(null=True, blank=True)
    goals_against = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-kickoff"]

    def __str__(self):
        return f"vs. {self.opponent}"

class MatchPerformance(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="performances")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="match_performances")
    minutes_played = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(130)])
    mentality = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    physicality = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    performance = models.PositiveSmallIntegerField(validators=SCORE_VALIDATORS)
    comment = models.CharField(max_length=300, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["match", "player"], name="unique_match_player")]

    @property
    def average(self):
        return round((self.mentality + self.physicality + self.performance) / 3, 1)

class ReportNote(models.Model):
    title = models.CharField(max_length=160, default="Interner Teamreport")
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
