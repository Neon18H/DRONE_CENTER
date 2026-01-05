from django.conf import settings
from django.db import models

from fleet.models import Drone
from ops.models import OperationSession


class AgentCommand(models.Model):
    class CommandType(models.TextChoices):
        START_MISSION = "START_MISSION", "Start Mission"
        END_MISSION = "END_MISSION", "End Mission"
        RETURN_HOME = "RETURN_HOME", "Return Home"
        PING = "PING", "Ping"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        ACKED = "ACKED", "Acked"
        FAILED = "FAILED", "Failed"

    drone = models.ForeignKey(Drone, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    session = models.ForeignKey(OperationSession, on_delete=models.SET_NULL, null=True, blank=True)
    command = models.CharField(max_length=30, choices=CommandType.choices)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    acked_at = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.drone.serial} - {self.command} ({self.status})"
