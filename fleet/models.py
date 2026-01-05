from django.db import models


class Drone(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        IN_USE = "IN_USE", "In Use"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        LOST_LINK = "LOST_LINK", "Lost Link"

    serial = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    last_seen = models.DateTimeField(null=True, blank=True)
    firmware = models.CharField(max_length=100, blank=True)
    camera_type = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.serial} - {self.model}"
