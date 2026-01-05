from django.urls import path

from .views import (
    RouteCreateView,
    RouteDeleteView,
    RouteListView,
    RouteUpdateView,
    ShiftCreateView,
    ShiftDeleteView,
    ShiftListView,
    ShiftUpdateView,
    operation_notes,
)

urlpatterns = [
    path("admin/routes/", RouteListView.as_view(), name="admin-route-list"),
    path("admin/routes/create/", RouteCreateView.as_view(), name="admin-route-create"),
    path("admin/routes/<int:pk>/edit/", RouteUpdateView.as_view(), name="admin-route-update"),
    path("admin/routes/<int:pk>/delete/", RouteDeleteView.as_view(), name="admin-route-delete"),
    path("admin/shifts/", ShiftListView.as_view(), name="admin-shift-list"),
    path("admin/shifts/create/", ShiftCreateView.as_view(), name="admin-shift-create"),
    path("admin/shifts/<int:pk>/edit/", ShiftUpdateView.as_view(), name="admin-shift-update"),
    path("admin/shifts/<int:pk>/delete/", ShiftDeleteView.as_view(), name="admin-shift-delete"),
    path("pilot/operation/<int:session_id>/notes/", operation_notes, name="pilot-operation-notes"),
]
