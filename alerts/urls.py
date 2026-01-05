from django.urls import path

from .views import (
    AdminAlertListView,
    create_alert,
    mark_alert_read,
    pilot_inbox,
    update_alert_assignment,
    update_alert_status,
)

urlpatterns = [
    path("admin/", AdminAlertListView.as_view(), name="admin-alert-list"),
    path("admin/<int:alert_id>/status/<str:status>/", update_alert_status, name="admin-alert-status"),
    path("admin/<int:alert_id>/update/", update_alert_assignment, name="admin-alert-update"),
    path("pilot/create/", create_alert, name="pilot-alert-create"),
    path("pilot/inbox/", pilot_inbox, name="pilot-alert-inbox"),
    path("pilot/inbox/<int:alert_id>/read/", mark_alert_read, name="pilot-alert-read"),
]
