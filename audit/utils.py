from django.db.utils import OperationalError, ProgrammingError

from .models import AuditLog


def log_event(actor, action, object_type, object_id, request=None, metadata=None):
    try:
        ip = ""
        if request:
            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            if forwarded_for:
                ip = forwarded_for.split(",")[0].strip()
            else:
                ip = request.META.get("REMOTE_ADDR", "")
        return AuditLog.objects.create(
            actor=actor,
            action=action,
            object_type=object_type,
            object_id=object_id,
            ip=ip,
            metadata=metadata or {},
        )
    except (OperationalError, ProgrammingError):
        return None
