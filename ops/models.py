from django.conf import settings
from django.db import models

from fleet.models import Drone


class Route(models.Model):
    class RiskLevels(models.TextChoices):
        LOW = "LOW", "Low"
        MED = "MED", "Medium"
        HIGH = "HIGH", "High"

    name = models.CharField(max_length=100)
    zone_geojson = models.JSONField()
    waypoints = models.JSONField()
    risk_level = models.CharField(max_length=10, choices=RiskLevels.choices, default=RiskLevels.LOW)

    def __str__(self) -> str:
        return self.name


class Shift(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        ACTIVE = "ACTIVE", "Active"
        DONE = "DONE", "Done"
        CANCELLED = "CANCELLED", "Cancelled"

    pilot = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    drone = models.ForeignKey(Drone, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    def __str__(self) -> str:
        return f"{self.pilot.username} - {self.start_at:%Y-%m-%d %H:%M}"


class OperationSession(models.Model):
    class Status(models.TextChoices):
        RUNNING = "RUNNING", "Running"
        ENDED = "ENDED", "Ended"

    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Session {self.shift_id} - {self.status}"
