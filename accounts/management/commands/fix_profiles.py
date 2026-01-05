from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import OperationalError, ProgrammingError

from accounts.models import Profile


class Command(BaseCommand):
    help = "Create missing Profile records for existing users."

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            users = User.objects.all()
            created_count = 0
            for user in users:
                _, created = Profile.objects.get_or_create(user=user)
                if created:
                    created_count += 1
        except (OperationalError, ProgrammingError) as exc:
            self.stderr.write(
                self.style.ERROR(
                    f"Cannot create profiles before migrations are applied: {exc}"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Profiles ensured. Newly created: {created_count}."
            )
        )
