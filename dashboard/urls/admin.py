from django.urls import path

from dashboard.views import admin_dashboard

urlpatterns = [
    path("dashboard/", admin_dashboard, name="admin-dashboard"),
]
