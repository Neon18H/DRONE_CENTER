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
    api_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_lat = models.FloatField(null=True, blank=True)
    last_lng = models.FloatField(null=True, blank=True)
    last_alt = models.FloatField(null=True, blank=True)
    last_battery = models.IntegerField(null=True, blank=True)
    last_signal = models.IntegerField(null=True, blank=True)
    last_heading = models.IntegerField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    firmware = models.CharField(max_length=100, blank=True)
    camera_type = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.serial} - {self.model}"
