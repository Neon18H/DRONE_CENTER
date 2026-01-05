from django.urls import path

from alerts.views import AdminAlertListView
from dashboard.views import admin_dashboard
from ops.views import DispatchCreateView, activate_shift, cancel_shift

urlpatterns = [
    path("dashboard/", admin_dashboard, name="admin-dashboard"),
    path("dispatch/", DispatchCreateView.as_view(), name="admin-dispatch"),
    path("alerts/", AdminAlertListView.as_view(), name="admin-alert-center"),
    path("shifts/<int:shift_id>/activate/", activate_shift, name="admin-shift-activate"),
    path("shifts/<int:shift_id>/cancel/", cancel_shift, name="admin-shift-cancel"),
]
