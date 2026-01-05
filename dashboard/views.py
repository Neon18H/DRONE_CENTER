from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from alerts.forms import AlertForm
from alerts.models import Alert
from audit.models import AuditLog
from audit.utils import log_event
from fleet.models import Drone
from integrations.models import AgentCommand
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
    requires_migrations = False
    try:
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
        last_command = (
            AgentCommand.objects.filter(drone=shift.drone).order_by("-created_at").first()
            if shift
            else None
        )
    except (OperationalError, ProgrammingError):
        requires_migrations = True
        shift = None
        current_session = None
        alert_form = AlertForm()
        alerts_received = []
        last_command = None

    agent_online = False
    if shift and shift.drone.last_seen:
        agent_online = shift.drone.last_seen >= now - timedelta(minutes=10)

    return render(
        request,
        "dashboard/pilot_dashboard.html",
        {
            "requires_migrations": requires_migrations,
            "shift": shift,
            "now": now,
            "current_session": current_session,
            "alert_form": alert_form,
            "alerts_received": alerts_received,
            "agent_online": agent_online,
            "last_command": last_command,
        },
    )


@login_required
@role_required("PILOT")
def pilot_operation_view(request):
    now = timezone.now()
    try:
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
    except (OperationalError, ProgrammingError):
        messages.error(request, "No hay datos disponibles. Ejecuta las migraciones.")
        return redirect("pilot-dashboard")

    if not shift:
        messages.error(request, "No tienes un turno asignado.")
        return redirect("pilot-dashboard")

    current_session = OperationSession.objects.filter(
        shift=shift, status=OperationSession.Status.RUNNING
    ).first()
    last_command = AgentCommand.objects.filter(drone=shift.drone).order_by("-created_at").first()
    alert_form = AlertForm()

    agent_online = False
    if shift.drone.last_seen:
        agent_online = shift.drone.last_seen >= now - timedelta(minutes=10)

    operation_state = (
        OperationSession.Status.RUNNING if current_session else OperationSession.Status.ENDED
    )
    awaiting_ack = bool(
        last_command
        and last_command.status in [AgentCommand.Status.PENDING, AgentCommand.Status.SENT]
    )
    command_feedback = "Awaiting drone ACK..." if awaiting_ack else None
    control_status = (
        "LIVE / CONTROL ACTIVE"
        if last_command and last_command.status == AgentCommand.Status.ACKED
        else None
    )

    return render(
        request,
        "pilot/operation.html",
        {
            "shift": shift,
            "current_session": current_session,
            "operation_state": operation_state,
            "agent_online": agent_online,
            "last_command": last_command,
            "command_feedback": command_feedback,
            "control_status": control_status,
            "alert_form": alert_form,
        },
    )


@login_required
@role_required("PILOT")
def pilot_operation_telemetry_partial(request):
    try:
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
    except (OperationalError, ProgrammingError):
        shift = None

    drone = shift.drone if shift else None
    return render(request, "pilot/partials/telemetry.html", {"drone": drone})


@login_required
@role_required("PILOT")
@require_POST
def start_operation(request):
    try:
        shift = (
            Shift.objects.filter(
                pilot=request.user, status__in=[Shift.Status.SCHEDULED, Shift.Status.ACTIVE]
            )
            .order_by("start_at")
            .first()
        )
    except (OperationalError, ProgrammingError):
        messages.error(request, "No hay datos disponibles. Ejecuta las migraciones.")
        return redirect("pilot-dashboard")
    if not shift:
        messages.error(request, "No tienes un turno asignado.")
        return redirect("pilot-dashboard")

    if OperationSession.objects.filter(shift=shift, status=OperationSession.Status.RUNNING).exists():
        messages.warning(request, "Ya existe una operación en curso.")
        return redirect("pilot-operation-center")

    if (
        shift.drone.status == Drone.Status.IN_USE
        and Shift.objects.filter(drone=shift.drone, status=Shift.Status.ACTIVE)
        .exclude(pilot=request.user)
        .exists()
    ):
        messages.error(request, "El dron ya está en uso por otro turno.")
        return redirect("pilot-dashboard")

    now = timezone.now()
    if not (shift.start_at <= now <= shift.end_at):
        messages.error(request, "El turno no está en ventana de operación.")
        return redirect("pilot-dashboard")

    try:
        with transaction.atomic():
            session = OperationSession.objects.create(shift=shift, started_at=now)
            shift.status = Shift.Status.ACTIVE
            shift.save(update_fields=["status"])
            Drone.objects.filter(id=shift.drone_id).update(status=Drone.Status.IN_USE)
            payload = {
                "session_id": session.id,
                "route_name": shift.route.name,
                "waypoints": shift.route.waypoints,
                "zone_geojson": shift.route.zone_geojson,
            }
            command = AgentCommand.objects.create(
                drone=shift.drone,
                created_by=request.user,
                session=session,
                command=AgentCommand.CommandType.START_MISSION,
                payload=payload,
            )
            log_event(request.user, "start_operation", "OperationSession", str(session.id), request)
            log_event(
                request.user,
                "enqueue_command",
                "AgentCommand",
                str(command.id),
                request,
                metadata={"command": command.command},
            )
    except (OperationalError, ProgrammingError):
        messages.error(request, "No se pudo iniciar la operación. Ejecuta migraciones.")
        return redirect("pilot-dashboard")

    messages.success(request, "Operación iniciada. Comando enviado al dron.")
    return redirect("pilot-operation-center")


@login_required
@role_required("PILOT")
@require_POST
def end_operation(request):
    try:
        shift = (
            Shift.objects.filter(pilot=request.user, status=Shift.Status.ACTIVE)
            .order_by("start_at")
            .first()
        )
    except (OperationalError, ProgrammingError):
        messages.error(request, "No hay datos disponibles. Ejecuta las migraciones.")
        return redirect("pilot-dashboard")
    if not shift:
        messages.error(request, "No hay operación activa.")
        return redirect("pilot-dashboard")

    session = (
        OperationSession.objects.filter(shift=shift, status=OperationSession.Status.RUNNING)
        .order_by("started_at")
        .first()
    )
    if not session:
        messages.error(request, "No hay sesión activa.")
        return redirect("pilot-dashboard")

    try:
        with transaction.atomic():
            session.status = OperationSession.Status.ENDED
            session.ended_at = timezone.now()
            session.save(update_fields=["status", "ended_at"])
            shift.status = Shift.Status.DONE
            shift.save(update_fields=["status"])
            Drone.objects.filter(id=shift.drone_id).update(status=Drone.Status.AVAILABLE)
            command = AgentCommand.objects.create(
                drone=shift.drone,
                created_by=request.user,
                session=session,
                command=AgentCommand.CommandType.END_MISSION,
                payload={"session_id": session.id},
            )
            log_event(request.user, "end_operation", "OperationSession", str(session.id), request)
            log_event(
                request.user,
                "enqueue_command",
                "AgentCommand",
                str(command.id),
                request,
                metadata={"command": command.command},
            )
    except (OperationalError, ProgrammingError):
        messages.error(request, "No se pudo finalizar la operación. Ejecuta migraciones.")
        return redirect("pilot-dashboard")

    messages.success(request, "Operación finalizada.")
    return redirect("pilot-dashboard")
