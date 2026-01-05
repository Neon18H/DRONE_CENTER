from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.views import View

from accounts.forms import PilotCreateForm, PilotUpdateForm
from accounts.models import Profile
from accounts.mixins import RoleRequiredMixin
from audit.utils import log_event

User = get_user_model()


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        form = AuthenticationForm(request)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_event(user, "login", "User", str(user.id), request)
            profile = getattr(user, "profile", None)
            if profile and profile.role == "ADMIN":
                return redirect("admin-dashboard")
            return redirect("pilot-dashboard")
        return render(request, self.template_name, {"form": form})


class UserLogoutView(LogoutView):
    next_page = "login"
    http_method_names = ["post"]


class LoginRedirectView(View):
    def get(self, request):
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == "ADMIN":
            return redirect("admin-dashboard")
        return redirect("pilot-dashboard")


class PilotListView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ("ADMIN",)
    template_name = "accounts/admin/pilots_list.html"

    def get(self, request):
        pilots = (
            User.objects.filter(profile__role=Profile.Roles.PILOT)
            .select_related("profile")
            .order_by("username")
        )
        return render(request, self.template_name, {"pilots": pilots})


class PilotCreateView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ("ADMIN",)
    template_name = "accounts/admin/pilot_form.html"

    def get(self, request):
        form = PilotCreateForm()
        return render(request, self.template_name, {"form": form, "title": "Crear piloto"})

    def post(self, request):
        form = PilotCreateForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "title": "Crear piloto"})

        password = form.cleaned_data["password"] or get_random_string(10)
        with transaction.atomic():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=password,
            )
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "role": Profile.Roles.PILOT,
                    "full_name": form.cleaned_data["full_name"],
                    "photo": form.cleaned_data["photo"],
                    "phone": form.cleaned_data["phone"],
                    "badge_id": form.cleaned_data["badge_id"],
                    "station": form.cleaned_data["station"],
                },
            )
        log_event(request.user, "create_pilot", "User", str(user.id), request)
        if not form.cleaned_data["password"]:
            messages.success(request, f"Piloto creado. Contraseña temporal: {password}")
        else:
            messages.success(request, "Piloto creado correctamente.")
        return redirect("admin-pilot-list")


class PilotUpdateView(LoginRequiredMixin, RoleRequiredMixin, View):
    allowed_roles = ("ADMIN",)
    template_name = "accounts/admin/pilot_form.html"

    def get(self, request, pilot_id):
        user = get_object_or_404(
            User.objects.filter(profile__role=Profile.Roles.PILOT).select_related("profile"),
            id=pilot_id,
        )
        form = PilotUpdateForm(
            user_instance=user,
            initial={
                "username": user.username,
                "email": user.email,
                "full_name": user.profile.full_name,
                "phone": user.profile.phone,
                "badge_id": user.profile.badge_id,
                "station": user.profile.station,
            },
        )
        return render(
            request,
            self.template_name,
            {"form": form, "title": "Editar piloto", "pilot": user},
        )

    def post(self, request, pilot_id):
        user = get_object_or_404(
            User.objects.filter(profile__role=Profile.Roles.PILOT).select_related("profile"),
            id=pilot_id,
        )
        form = PilotUpdateForm(request.POST, request.FILES, user_instance=user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "title": "Editar piloto", "pilot": user},
            )

        user.username = form.cleaned_data["username"]
        user.email = form.cleaned_data["email"]
        user.save(update_fields=["username", "email"])

        profile = user.profile
        profile.full_name = form.cleaned_data["full_name"]
        if form.cleaned_data["photo"]:
            profile.photo = form.cleaned_data["photo"]
        profile.phone = form.cleaned_data["phone"]
        profile.badge_id = form.cleaned_data["badge_id"]
        profile.station = form.cleaned_data["station"]
        profile.save()

        messages.success(request, "Piloto actualizado correctamente.")
        return redirect("admin-pilot-list")
