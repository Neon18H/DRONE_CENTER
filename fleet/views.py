from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.mixins import RoleRequiredMixin

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
