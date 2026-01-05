from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.views import View

from audit.utils import log_event


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


class LoginRedirectView(View):
    def get(self, request):
        profile = getattr(request.user, "profile", None)
        if profile and profile.role == "ADMIN":
            return redirect("admin-dashboard")
        return redirect("pilot-dashboard")
