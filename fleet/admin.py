import secrets

from django.contrib import admin
from django.utils.html import format_html

from .models import Drone

TOKEN_LENGTH = 64


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ("serial", "model", "status", "last_seen", "api_token_display")
    list_filter = ("status",)
    search_fields = ("serial", "model")
    actions = ("generate_api_token",)
    fieldsets = (
        (None, {"fields": ("serial", "model", "status")}),
        (
            "Telemetría",
            {
                "fields": (
                    "last_seen",
                    "last_lat",
                    "last_lng",
                    "last_alt",
                    "last_battery",
                    "last_signal",
                    "last_heading",
                )
            },
        ),
        ("Sistema", {"fields": ("firmware", "camera_type")}),
        ("API", {"fields": ("api_token",)}),
    )
    readonly_fields = (
        "last_seen",
        "last_lat",
        "last_lng",
        "last_alt",
        "last_battery",
        "last_signal",
        "last_heading",
    )

    @admin.display(description="API token")
    def api_token_display(self, obj):
        if not obj.api_token:
            return "-"
        return format_html('<span style="font-family: monospace;">{}</span>', obj.api_token)

    @admin.action(description="Generate API token")
    def generate_api_token(self, request, queryset):
        for drone in queryset:
            drone.api_token = secrets.token_hex(TOKEN_LENGTH // 2)
            drone.save(update_fields=["api_token"])
