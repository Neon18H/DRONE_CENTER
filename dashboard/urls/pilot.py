from django.urls import path

from dashboard.views import (
    end_operation,
    pilot_dashboard,
    pilot_operation_telemetry_partial,
    pilot_operation_view,
    start_operation,
)

urlpatterns = [
    path("dashboard/", pilot_dashboard, name="pilot-dashboard"),
    path("operation/", pilot_operation_view, name="pilot-operation-center"),
    path(
        "operation/telemetry/",
        pilot_operation_telemetry_partial,
        name="pilot-operation-telemetry",
    ),
    path("operation/start/", start_operation, name="pilot-operation-start"),
    path("operation/end/", end_operation, name="pilot-operation-end"),
]
