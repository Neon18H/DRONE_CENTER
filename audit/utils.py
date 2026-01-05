from .models import AuditLog


def log_event(actor, action, object_type, object_id, request=None, metadata=None):
    ip = ""
    if request:
        ip = request.META.get("REMOTE_ADDR", "")
    AuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=object_id,
        ip=ip,
        metadata=metadata or {},
    )
