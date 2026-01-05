from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_agent, name="agent-register"),
    path("telemetry/", views.telemetry, name="agent-telemetry"),
]
