import json

from django.core.exceptions import FieldDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from audit.utils import log_event
from fleet.models import Drone


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

    token = get_bearer_token(request)
    if not token:
        return json_error("missing_token", status=401)

    drone = find_drone_by_id(drone_id)
    if not drone:
        return json_error("drone_not_found", status=404)

    if not drone.api_token or drone.api_token != token:
        return json_error("invalid_token", status=401)

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

    token = get_bearer_token(request)
    if not token:
        return json_error("missing_token", status=401)

    drone = find_drone_by_id(drone_id)
    if not drone:
        return json_error("drone_not_found", status=404)

    if not drone.api_token or drone.api_token != token:
        return json_error("invalid_token", status=401)

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


# Example curl:
# curl -X POST https://XXXX.ngrok-free.app/api/agent/register/ \
#   -H "Authorization: Bearer TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{"drone_id":"DRX-001","agent_version":"1.0.0","mode":"SIMULATION","system":{}}'
