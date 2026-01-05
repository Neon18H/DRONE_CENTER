from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from accounts.mixins import RoleRequiredMixin

from .models import AuditLog


class AdminAuditListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = AuditLog
    template_name = "audit/admin_audit_list.html"
    context_object_name = "events"
    paginate_by = 25
    allowed_roles = ("ADMIN",)

    def get_queryset(self):
        return AuditLog.objects.order_by("-created_at")
