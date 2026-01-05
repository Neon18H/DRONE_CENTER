from django.contrib import admin

from .models import OperationSession, Route, Shift


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "risk_level")
    search_fields = ("name",)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("pilot", "drone", "route", "start_at", "end_at", "status")
    list_filter = ("status",)


@admin.register(OperationSession)
class OperationSessionAdmin(admin.ModelAdmin):
    list_display = ("shift", "status", "started_at", "ended_at")
