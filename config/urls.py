from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("dj-admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("admin/", include("dashboard.urls.admin")),
    path("pilot/", include("dashboard.urls.pilot")),
    path("fleet/", include("fleet.urls")),
    path("ops/", include("ops.urls")),
    path("alerts/", include("alerts.urls")),
    path("audit/", include("audit.urls")),
]
