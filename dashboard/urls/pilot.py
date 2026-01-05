from django.urls import path

from dashboard.views import pilot_dashboard

urlpatterns = [
    path("dashboard/", pilot_dashboard, name="pilot-dashboard"),
]
