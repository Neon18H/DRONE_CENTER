import secrets

from django import forms

from .models import Drone


class DroneForm(forms.ModelForm):
    class Meta:
        model = Drone
        fields = [
            "serial",
            "model",
            "status",
            "api_token",
            "video_url",
            "last_seen",
            "last_lat",
            "last_lng",
            "firmware",
            "camera_type",
        ]
        widgets = {
            "last_seen": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "api_token": forms.TextInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.api_token:
            instance.api_token = secrets.token_urlsafe(32)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
