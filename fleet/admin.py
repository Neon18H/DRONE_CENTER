from django.contrib import admin

from .models import Drone


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ("serial", "model", "status", "last_seen")
    list_filter = ("status",)
    search_fields = ("serial", "model")
