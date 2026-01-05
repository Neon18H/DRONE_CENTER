from django.contrib.auth.decorators import login_required
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import role_required
from alerts.forms import AlertForm
from alerts.models import Alert
from fleet.models import Drone
from ops.models import OperationSession, Shift


@login_required
@role_required("ADMIN")
def admin_dashboard(request):
    today = timezone.now().date()
    drones_available = Drone.objects.filter(status=Drone.Status.AVAILABLE).count()
    drones_in_use = Drone.objects.filter(status=Drone.Status.IN_USE).count()
    drones_maintenance = Drone.objects.filter(status=Drone.Status.MAINTENANCE).count()
    shifts_today = Shift.objects.filter(start_at__date=today).order_by("start_at")
    recent_alerts = Alert.objects.order_by("-created_at")[:10]

    return render(
        request,
        "dashboard/admin_dashboard.html",
        {
            "drones_available": drones_available,
            "drones_in_use": drones_in_use,
            "drones_maintenance": drones_maintenance,
            "shifts_today": shifts_today,
            "recent_alerts": recent_alerts,
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
