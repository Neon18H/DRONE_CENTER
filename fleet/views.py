from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import secrets

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.decorators import role_required
from accounts.mixins import RoleRequiredMixin
from audit.utils import log_event

from .forms import DroneForm
from .models import Drone


class DroneListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    model = Drone
    template_name = "fleet/admin_drone_list.html"
    context_object_name = "drones"
    allowed_roles = ("ADMIN",)


class DroneCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Drone
    form_class = DroneForm
    template_name = "fleet/drone_form.html"
    success_url = reverse_lazy("admin-drone-list")
    allowed_roles = ("ADMIN",)


class DroneUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Drone
    form_class = DroneForm
    template_name = "fleet/drone_form.html"
    success_url = reverse_lazy("admin-drone-list")
    allowed_roles = ("ADMIN",)


class DroneDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Drone
    template_name = "fleet/drone_confirm_delete.html"
    success_url = reverse_lazy("admin-drone-list")
    allowed_roles = ("ADMIN",)


@login_required
@role_required("ADMIN")
@require_POST
def mark_drone_status(request, drone_id, status):
    if status not in Drone.Status.values:
        return redirect("admin-drone-list")
    drone = get_object_or_404(Drone, id=drone_id)
    drone.status = status
    drone.save(update_fields=["status"])
    log_event(request.user, "update_drone_status", "Drone", str(drone.id), request, {"status": status})
    return redirect("admin-drone-list")


@login_required
@role_required("ADMIN")
@require_POST
def regenerate_drone_token(request, drone_id):
    drone = get_object_or_404(Drone, id=drone_id)
    drone.api_token = secrets.token_urlsafe(32)
    drone.save(update_fields=["api_token"])
    log_event(request.user, "regenerate_drone_token", "Drone", str(drone.id), request, {})
    return redirect("admin-drone-update", pk=drone.id)
