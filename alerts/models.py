from django.conf import settings
from django.db import models

from ops.models import OperationSession


class Alert(models.Model):
    class Categories(models.TextChoices):
        SUSPICIOUS = "SUSPICIOUS", "Suspicious"
        TRAFFIC = "TRAFFIC", "Traffic"
        THEFT = "THEFT", "Theft"
        EMERGENCY = "EMERGENCY", "Emergency"
        SUPPORT = "SUPPORT", "Support"
        OTHER = "OTHER", "Other"

    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MED = "MED", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACK = "ACK", "Acknowledged"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        RESOLVED = "RESOLVED", "Resolved"

    class Target(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PILOTS = "PILOTS", "Pilots"
        BOTH = "BOTH", "Both"

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(OperationSession, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=20, choices=Categories.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    target = models.CharField(max_length=10, choices=Target.choices)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.category} - {self.severity}"


class AlertRecipient(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Alert {self.alert_id} -> {self.recipient_user_id}"
