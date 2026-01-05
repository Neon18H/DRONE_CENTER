from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    try:
        profile, _ = Profile.objects.get_or_create(user=instance)
        desired_role = Profile.Roles.ADMIN if (instance.is_superuser or instance.is_staff) else Profile.Roles.PILOT
        if profile.role != desired_role:
            profile.role = desired_role
            profile.save(update_fields=["role"])
    except (OperationalError, ProgrammingError):
        return
