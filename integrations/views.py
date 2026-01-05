import json

from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from audit.utils import log_event
from fleet.models import Drone
from integrations.models import AgentCommand


def json_error(message, status):
    return JsonResponse({"ok": False, "error": message}, status=status)


def parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def get_bearer_token(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    return token or None


def find_drone_by_id(drone_id):
    lookup_field = "serial"
    try:
        Drone._meta.get_field("drone_id")
        lookup_field = "drone_id"
    except FieldDoesNotExist:
        pass
    return Drone.objects.filter(**{lookup_field: drone_id}).first()


def authorize_drone(request, drone_id):
    token = get_bearer_token(request)
    if not token:
        return None, json_error("missing_token", status=401)

    try:
        drone = find_drone_by_id(drone_id)
    except (OperationalError, ProgrammingError):
        return None, json_error("service_unavailable", status=503)

    if not drone:
        return None, json_error("drone_not_found", status=404)

    if not drone.api_token or drone.api_token != token:
        return None, json_error("invalid_token", status=401)

    return drone, None


@csrf_exempt
def register_agent(request):
    if request.method != "POST":
        return json_error("method_not_allowed", status=405)

    payload = parse_json_body(request)
    if payload is None:
        return json_error("invalid_json", status=400)

    drone_id = payload.get("drone_id")
    if not drone_id:
        return json_error("missing_drone_id", status=400)

    drone, error = authorize_drone(request, drone_id)
    if error:
        return error

    update_fields = {"last_seen": timezone.now()}
    agent_version = payload.get("agent_version")
    if agent_version:
        update_fields["firmware"] = agent_version

    for field, value in update_fields.items():
        setattr(drone, field, value)
    drone.save(update_fields=list(update_fields.keys()))

    log_event(
        actor=None,
        action="agent_register",
        object_type="Drone",
        object_id=str(drone.serial),
        request=request,
        metadata={"agent_version": agent_version, "mode": payload.get("mode")},
    )

    return JsonResponse({"ok": True, "message": "registered"})


@csrf_exempt
def telemetry(request):
    if request.method != "POST":
        return json_error("method_not_allowed", status=405)

    payload = parse_json_body(request)
    if payload is None:
        return json_error("invalid_json", status=400)

    drone_id = payload.get("drone_id")
    if not drone_id:
        return json_error("missing_drone_id", status=400)

    drone, error = authorize_drone(request, drone_id)
    if error:
        return error

    update_fields = {
        "last_lat": payload.get("lat"),
        "last_lng": payload.get("lng"),
        "last_alt": payload.get("alt"),
        "last_battery": payload.get("battery"),
        "last_signal": payload.get("signal"),
        "last_heading": payload.get("heading"),
        "last_seen": timezone.now(),
    }

    status = payload.get("status")
    if status in {"LOST_LINK", "NO_SIGNAL"}:
        update_fields["status"] = Drone.Status.LOST_LINK

    for field, value in update_fields.items():
        setattr(drone, field, value)
    drone.save(update_fields=list(update_fields.keys()))

    return JsonResponse({"ok": True})


@csrf_exempt
def pull_commands(request):
    if request.method != "GET":
        return json_error("method_not_allowed", status=405)

    drone_id = request.GET.get("drone_id")
    if not drone_id:
        return json_error("missing_drone_id", status=400)

    drone, error = authorize_drone(request, drone_id)
    if error:
        return error

    try:
        with transaction.atomic():
            command = (
                AgentCommand.objects.select_for_update()
                .filter(drone=drone, status=AgentCommand.Status.PENDING)
                .order_by("created_at")
                .first()
            )
            if not command:
                return JsonResponse({"ok": True, "command": None})
            command.status = AgentCommand.Status.SENT
            command.sent_at = timezone.now()
            command.save(update_fields=["status", "sent_at"])
    except (OperationalError, ProgrammingError):
        return JsonResponse({"ok": True, "command": None})

    return JsonResponse(
        {
            "ok": True,
            "command": {
                "id": command.id,
                "command": command.command,
                "payload": command.payload,
            },
        }
    )


@csrf_exempt
def ack_command(request):
    if request.method != "POST":
        return json_error("method_not_allowed", status=405)

    payload = parse_json_body(request)
    if payload is None:
        return json_error("invalid_json", status=400)

    drone_id = payload.get("drone_id")
    if not drone_id:
        return json_error("missing_drone_id", status=400)

    drone, error = authorize_drone(request, drone_id)
    if error:
        return error

    command_id = payload.get("command_id")
    status = payload.get("status")
    if not command_id:
        return json_error("missing_command_id", status=400)

    if status not in {AgentCommand.Status.ACKED, AgentCommand.Status.FAILED}:
        return json_error("invalid_status", status=400)

    try:
        command = AgentCommand.objects.get(id=command_id, drone=drone)
    except AgentCommand.DoesNotExist:
        return json_error("command_not_found", status=404)
    except (OperationalError, ProgrammingError):
        return json_error("service_unavailable", status=503)

    command.status = status
    command.acked_at = timezone.now()
    command.result = payload.get("result") or {}
    command.save(update_fields=["status", "acked_at", "result"])

    log_event(
        actor=None,
        action="agent_ack",
        object_type="AgentCommand",
        object_id=str(command.id),
        request=request,
        metadata={"status": status, "drone_id": drone.serial},
    )

    return JsonResponse({"ok": True})


# Example curl:
# curl -X POST https://XXXX.ngrok-free.app/api/agent/register/ \
#   -H "Authorization: Bearer TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{"drone_id":"DRX-001","agent_version":"1.0.0","mode":"SIMULATION","system":{}}'
