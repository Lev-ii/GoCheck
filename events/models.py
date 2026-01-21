import uuid
from django.conf import settings
from django.db import models
from teams.models import Team
from checklists.models import ChecklistTemplate


class Event(models.Model):
    class Visibility(models.TextChoices):
        PERSONAL = "PERSONAL", "Personal"
        TEAM = "TEAM", "Team"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=160)

    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PERSONAL)
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="events_owned"
    )
    owner_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, blank=True, related_name="events"
    )

    starts_at = models.DateTimeField()
    location = models.CharField(max_length=180, null=True, blank=True)

    is_recurring = models.BooleanField(default=False)
    rrule = models.CharField(max_length=255, null=True, blank=True)  # ex: "FREQ=WEEKLY;BYDAY=SU;BYHOUR=6;BYMINUTE=30"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class EventTemplateLink(models.Model):
    class Kind(models.TextChoices):
        SETUP = "SETUP", "Setup"
        TEARDOWN = "TEARDOWN", "Teardown"
        GENERIC = "GENERIC", "Generic"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="template_links")
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.CASCADE, related_name="event_links")
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.GENERIC)

    class Meta:
        unique_together = ("event", "template", "kind")


class EventOccurrence(models.Model):
    class Status(models.TextChoices):
        UPCOMING = "UPCOMING", "Upcoming"
        ACTIVE = "ACTIVE", "Active"
        DONE = "DONE", "Done"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="occurrences")
    starts_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UPCOMING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.title} @ {self.starts_at}"


class OccurrenceChecklist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    occurrence = models.ForeignKey(EventOccurrence, on_delete=models.CASCADE, related_name="checklists")
    template = models.ForeignKey(ChecklistTemplate, on_delete=models.PROTECT, related_name="occurrence_checklists")

    progress_cache = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class OccurrenceChecklistItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    occurrence_checklist = models.ForeignKey(OccurrenceChecklist, on_delete=models.CASCADE, related_name="items")

    template_item_id = models.UUIDField(null=True, blank=True)
    label_snapshot = models.CharField(max_length=200)
    position = models.PositiveIntegerField(default=0)

    is_checked = models.BooleanField(default=False)

    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="items_checked"
    )
    checked_at = models.DateTimeField(null=True, blank=True)

    unchecked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="items_unchecked"
    )
    unchecked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position"]
