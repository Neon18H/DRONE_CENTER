from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin
from audit.utils import log_event
from fleet.models import Drone

from .forms import OperationSessionForm, RouteForm, ShiftForm
from .models import OperationSession, Route, Shift


class RouteListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Route
    template_name = "ops/admin_route_list.html"
    context_object_name = "routes"
    allowed_roles = ("ADMIN",)


class RouteCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Route
    form_class = RouteForm
    template_name = "ops/route_form.html"
    success_url = reverse_lazy("admin-route-list")
    allowed_roles = ("ADMIN",)


class RouteUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Route
    form_class = RouteForm
    template_name = "ops/route_form.html"
    success_url = reverse_lazy("admin-route-list")
    allowed_roles = ("ADMIN",)


class RouteDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Route
    template_name = "ops/route_confirm_delete.html"
    success_url = reverse_lazy("admin-route-list")
    allowed_roles = ("ADMIN",)


class ShiftListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Shift
    template_name = "ops/admin_shift_list.html"
    context_object_name = "shifts"
    allowed_roles = ("ADMIN",)


class ShiftCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Shift
    form_class = ShiftForm
    template_name = "ops/shift_form.html"
    success_url = reverse_lazy("admin-shift-list")
    allowed_roles = ("ADMIN",)

    def form_valid(self, form):
        response = super().form_valid(form)
        log_event(self.request.user, "create_shift", "Shift", str(self.object.id), self.request)
        return response


class ShiftUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Shift
    form_class = ShiftForm
    template_name = "ops/shift_form.html"
    success_url = reverse_lazy("admin-shift-list")
    allowed_roles = ("ADMIN",)


class ShiftDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Shift
    template_name = "ops/shift_confirm_delete.html"
    success_url = reverse_lazy("admin-shift-list")
    allowed_roles = ("ADMIN",)


@login_required
@role_required("PILOT")
def start_operation(request):
    shift = (
        Shift.objects.filter(pilot=request.user, status__in=[Shift.Status.SCHEDULED, Shift.Status.ACTIVE])
        .order_by("start_at")
        .first()
    )
    if not shift:
        messages.error(request, "No tienes un turno asignado.")
        return redirect("pilot-dashboard")

    if OperationSession.objects.filter(shift=shift, status=OperationSession.Status.RUNNING).exists():
        messages.warning(request, "Ya existe una operación en curso.")
        return redirect("pilot-dashboard")

    now = timezone.now()
    if not (shift.start_at <= now <= shift.end_at):
        messages.error(request, "El turno no está en ventana de operación.")
        return redirect("pilot-dashboard")

    with transaction.atomic():
        session = OperationSession.objects.create(shift=shift, started_at=now)
        shift.status = Shift.Status.ACTIVE
        shift.save(update_fields=["status"])
        Drone.objects.filter(id=shift.drone_id).update(status=Drone.Status.IN_USE)
        log_event(request.user, "start_operation", "OperationSession", str(session.id), request)

    messages.success(request, "Operación iniciada.")
    return redirect("pilot-dashboard")


@login_required
@role_required("PILOT")
def end_operation(request):
    shift = (
        Shift.objects.filter(pilot=request.user, status=Shift.Status.ACTIVE)
        .order_by("start_at")
        .first()
    )
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

    with transaction.atomic():
        session.status = OperationSession.Status.ENDED
        session.ended_at = timezone.now()
        session.save(update_fields=["status", "ended_at"])
        shift.status = Shift.Status.DONE
        shift.save(update_fields=["status"])
        Drone.objects.filter(id=shift.drone_id).update(status=Drone.Status.AVAILABLE)
        log_event(request.user, "end_operation", "OperationSession", str(session.id), request)

    messages.success(request, "Operación finalizada.")
    return redirect("pilot-dashboard")


@login_required
@role_required("PILOT")
def operation_notes(request, session_id):
    session = get_object_or_404(OperationSession, id=session_id, shift__pilot=request.user)
    if request.method == "POST":
        form = OperationSessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, "Notas actualizadas.")
            return redirect("pilot-dashboard")
    else:
        form = OperationSessionForm(instance=session)
    return render(request, "ops/operation_notes_form.html", {"form": form, "session": session})
