from django.urls import path

from .views import (
    LoginRedirectView,
    LoginView,
    PilotCreateView,
    PilotListView,
    PilotUpdateView,
    UserLogoutView,
)

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path("redirect/", LoginRedirectView.as_view(), name="login-redirect"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("admin/pilots/", PilotListView.as_view(), name="admin-pilot-list"),
    path("admin/pilots/create/", PilotCreateView.as_view(), name="admin-pilot-create"),
    path("admin/pilots/<int:pilot_id>/edit/", PilotUpdateView.as_view(), name="admin-pilot-edit"),
]
