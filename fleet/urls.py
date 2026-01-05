from django.urls import path

from .views import (
    DroneCreateView,
    DroneDeleteView,
    DroneListView,
    DroneUpdateView,
    mark_drone_status,
    regenerate_drone_token,
)

urlpatterns = [
    path("admin/drones/", DroneListView.as_view(), name="admin-drone-list"),
    path("admin/drones/create/", DroneCreateView.as_view(), name="admin-drone-create"),
    path("admin/drones/<int:pk>/edit/", DroneUpdateView.as_view(), name="admin-drone-update"),
    path("admin/drones/<int:pk>/delete/", DroneDeleteView.as_view(), name="admin-drone-delete"),
    path("admin/drones/<int:drone_id>/status/<str:status>/", mark_drone_status, name="admin-drone-status"),
    path(
        "admin/drones/<int:drone_id>/regenerate-token/",
        regenerate_drone_token,
        name="admin-drone-regenerate-token",
    ),
]
