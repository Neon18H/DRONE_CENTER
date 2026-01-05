from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin
from audit.utils import log_event

from .forms import AlertAdminUpdateForm, AlertForm
from .models import Alert, AlertComment, AlertRecipient


class AdminAlertListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Alert
    template_name = "alerts/admin_alert_list.html"
    context_object_name = "alerts"
    allowed_roles = ("ADMIN",)

    def get_queryset(self):
        queryset = Alert.objects.order_by("-created_at")
        status = self.request.GET.get("status")
        severity = self.request.GET.get("severity")
        category = self.request.GET.get("category")
        if status:
            queryset = queryset.filter(status=status)
        if severity:
            queryset = queryset.filter(severity=severity)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assignable_users"] = get_user_model().objects.filter(is_active=True).order_by("username")
        context["update_form"] = AlertAdminUpdateForm()
        context["alert_model"] = Alert
        return context


@login_required
@role_required("ADMIN")
@require_POST
def update_alert_status(request, alert_id, status):
    alert = get_object_or_404(Alert, id=alert_id)
    if status not in Alert.Status.values:
        messages.error(request, "Estado inválido.")
        return redirect(request.POST.get("next") or "admin-alert-list")
    alert.status = status
    alert.save(update_fields=["status"])
    log_event(request.user, "update_alert_status", "Alert", str(alert.id), request, {"status": status})
    messages.success(request, "Estado actualizado.")
    return redirect(request.POST.get("next") or "admin-alert-list")


@login_required
@role_required("ADMIN")
@require_POST
def update_alert_assignment(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    form = AlertAdminUpdateForm(request.POST, instance=alert)
    if form.is_valid():
        alert = form.save()
        comment = form.cleaned_data.get("internal_comment")
        if comment:
            AlertComment.objects.create(alert=alert, created_by=request.user, body=comment)
        log_event(
            request.user,
            "update_alert",
            "Alert",
            str(alert.id),
            request,
            {"status": alert.status, "assigned_to": alert.assigned_to_id},
        )
        messages.success(request, "Alerta actualizada.")
    else:
        messages.error(request, "No se pudo actualizar la alerta.")
    return redirect(request.POST.get("next") or "admin-alert-list")


@login_required
@role_required("PILOT")
def create_alert(request):
    if request.method == "POST":
        form = AlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.created_by = request.user
            alert.save()
            log_event(request.user, "create_alert", "Alert", str(alert.id), request)
            messages.success(request, "Alerta enviada.")
            return redirect("pilot-dashboard")
    else:
        form = AlertForm()
    return render(request, "alerts/pilot_alert_form.html", {"form": form})


@login_required
@role_required("PILOT")
def pilot_inbox(request):
    alerts = Alert.objects.filter(
        Q(target__in=[Alert.Target.PILOTS, Alert.Target.BOTH])
        | Q(alertrecipient__recipient_user=request.user)
    ).distinct().order_by("-created_at")
    return render(request, "alerts/pilot_inbox.html", {"alerts": alerts})


@login_required
@role_required("PILOT")
def mark_alert_read(request, alert_id):
    recipient, _created = AlertRecipient.objects.get_or_create(alert_id=alert_id, recipient_user=request.user)
    recipient.read_at = timezone.now()
    recipient.save(update_fields=["read_at"])
    return redirect("pilot-alert-inbox")
