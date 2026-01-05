from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from fleet.models import Drone
from ops.models import Route, Shift


class Command(BaseCommand):
    help = "Seed demo data for DRONEX"

    def handle(self, *args, **options):
        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@dronex.local"})
        if not admin.check_password("admin1234"):
            admin.set_password("admin1234")
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
        Profile.objects.filter(user=admin).update(role=Profile.Roles.ADMIN)

        pilots = []
        for idx in range(1, 6):
            username = f"pilot{idx}"
            pilot, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@dronex.local"})
            if not pilot.check_password("pilot1234"):
                pilot.set_password("pilot1234")
                pilot.save()
            Profile.objects.filter(user=pilot).update(role=Profile.Roles.PILOT)
            pilots.append(pilot)

        statuses = [Drone.Status.AVAILABLE, Drone.Status.IN_USE, Drone.Status.MAINTENANCE, Drone.Status.LOST_LINK]
        drones = []
        for idx in range(1, 11):
            drone, _ = Drone.objects.get_or_create(
                serial=f"DRX-{idx:03d}",
                defaults={
                    "model": f"Falcon-{idx}",
                    "status": statuses[idx % len(statuses)],
                    "firmware": "v1.0",
                    "camera_type": "4K",
                },
            )
            drones.append(drone)

        routes = []
        for idx in range(1, 6):
            route, _ = Route.objects.get_or_create(
                name=f"Ruta {idx}",
                defaults={
                    "zone_geojson": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
                    "waypoints": [{"lat": 0.0, "lng": 0.0}, {"lat": 1.0, "lng": 1.0}],
                    "risk_level": Route.RiskLevels.MED,
                },
            )
            routes.append(route)

        now = timezone.now()
        for idx in range(5):
            Shift.objects.get_or_create(
                pilot=pilots[idx],
                drone=drones[idx],
                route=routes[idx % len(routes)],
                defaults={
                    "start_at": now.replace(hour=8 + idx, minute=0, second=0, microsecond=0),
                    "end_at": now.replace(hour=10 + idx, minute=0, second=0, microsecond=0),
                    "status": Shift.Status.SCHEDULED,
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed data created."))
