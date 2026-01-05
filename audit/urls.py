from django.urls import path

from .views import AdminAuditListView

urlpatterns = [
    path("admin/", AdminAuditListView.as_view(), name="admin-audit-list"),
]
