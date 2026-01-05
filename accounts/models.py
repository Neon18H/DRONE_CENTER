from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PILOT = "PILOT", "Pilot"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.PILOT)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
