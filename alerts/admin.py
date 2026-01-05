from django.contrib import admin

from .models import Alert, AlertRecipient


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("category", "severity", "status", "target", "created_at")
    list_filter = ("status", "severity", "category", "target")
    search_fields = ("description",)


@admin.register(AlertRecipient)
class AlertRecipientAdmin(admin.ModelAdmin):
    list_display = ("alert", "recipient_user", "read_at")
