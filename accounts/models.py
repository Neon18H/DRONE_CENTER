from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PILOT = "PILOT", "Pilot"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.PILOT)
    full_name = models.CharField(max_length=150, default="")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    badge_id = models.CharField(max_length=50, blank=True)
    station = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
