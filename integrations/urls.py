from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register_agent, name="agent-register"),
    path("telemetry/", views.telemetry, name="agent-telemetry"),
    path("commands/pull/", views.pull_commands, name="agent-commands-pull"),
    path("ack/", views.ack_command, name="agent-commands-ack"),
]
