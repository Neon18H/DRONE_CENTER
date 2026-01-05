from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import role_required
from alerts.forms import AlertForm
from alerts.models import Alert
from audit.models import AuditLog
from fleet.models import Drone
from ops.models import OperationSession, Route, Shift


@login_required
@role_required("ADMIN")
def admin_dashboard(request):
    now = timezone.now()
    today = now.date()
    requires_migrations = False
    try:
        online_threshold = now - timedelta(minutes=10)
        drones_online = Drone.objects.filter(last_seen__gte=online_threshold).count()
        drones_available = Drone.objects.filter(status=Drone.Status.AVAILABLE).count()
        drones_in_use = Drone.objects.filter(status=Drone.Status.IN_USE).count()
        drones_maintenance = Drone.objects.filter(status=Drone.Status.MAINTENANCE).count()
        drones_lost_link = Drone.objects.filter(status=Drone.Status.LOST_LINK).count()
        pilots_active = (
            Shift.objects.filter(status=Shift.Status.ACTIVE).values("pilot_id").distinct().count()
        )
        alerts_open = Alert.objects.filter(status=Alert.Status.OPEN).count()
        alerts_critical = Alert.objects.filter(severity=Alert.Severity.CRITICAL).count()
        shifts_today = Shift.objects.filter(start_at__date=today).order_by("start_at")[:10]
        alert_queue = Alert.objects.order_by("-created_at")
        audit_events = AuditLog.objects.order_by("-created_at")[:20]
        drones_map = list(
            Drone.objects.exclude(last_lat__isnull=True, last_lng__isnull=True)
            .values("id", "serial", "status", "last_lat", "last_lng", "last_seen")
            .order_by("serial")
        )
        active_routes = list(
            Route.objects.filter(shift__status=Shift.Status.ACTIVE)
            .values("id", "name", "zone_geojson")
            .distinct()
        )
    except (OperationalError, ProgrammingError):
        requires_migrations = True
        drones_online = drones_available = drones_in_use = drones_maintenance = drones_lost_link = 0
        pilots_active = alerts_open = alerts_critical = 0
        shifts_today = []
        alert_queue = []
        audit_events = []
        drones_map = []
        active_routes = []

    status_filter = request.GET.get("status")
    severity_filter = request.GET.get("severity")
    category_filter = request.GET.get("category")
    if not requires_migrations:
        if status_filter:
            alert_queue = alert_queue.filter(status=status_filter)
        if severity_filter:
            alert_queue = alert_queue.filter(severity=severity_filter)
        if category_filter:
            alert_queue = alert_queue.filter(category=category_filter)
        alert_queue = alert_queue[:10]

    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "requires_migrations": requires_migrations,
            "now": now,
            "online_threshold": online_threshold if not requires_migrations else None,
            "drones_online": drones_online,
            "drones_available": drones_available,
            "drones_in_use": drones_in_use,
            "drones_maintenance": drones_maintenance,
            "drones_lost_link": drones_lost_link,
            "pilots_active": pilots_active,
            "alerts_open": alerts_open,
            "alerts_critical": alerts_critical,
            "shifts_today": shifts_today,
            "alert_queue": alert_queue,
            "audit_events": audit_events,
            "drones_map": drones_map,
            "active_routes": active_routes,
            "alert_model": Alert,
            "status_filter": status_filter or "",
            "severity_filter": severity_filter or "",
            "category_filter": category_filter or "",
        },
    )


@login_required
@role_required("PILOT")
def pilot_dashboard(request):
    now = timezone.now()
    shift = (
        Shift.objects.filter(pilot=request.user)
        .exclude(status=Shift.Status.CANCELLED)
        .annotate(
            status_priority=Case(
                When(status=Shift.Status.ACTIVE, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        .order_by("status_priority", "start_at")
        .first()
    )
    current_session = None
    if shift:
        current_session = OperationSession.objects.filter(
            shift=shift, status=OperationSession.Status.RUNNING
        ).first()
    alert_form = AlertForm()
    alerts_received = (
        Alert.objects.filter(
            Q(target__in=[Alert.Target.PILOTS, Alert.Target.BOTH])
            | Q(alertrecipient__recipient_user=request.user)
        )
        .distinct()
        .order_by("-created_at")[:5]
    )

    return render(
        request,
        "dashboard/pilot_dashboard.html",
        {
            "shift": shift,
            "now": now,
            "current_session": current_session,
            "alert_form": alert_form,
            "alerts_received": alerts_received,
        },
    )
