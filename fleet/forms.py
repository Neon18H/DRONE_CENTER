from django import forms

from .models import Drone


class DroneForm(forms.ModelForm):
    class Meta:
        model = Drone
        fields = [
            "serial",
            "model",
            "status",
            "last_seen",
            "firmware",
            "camera_type",
        ]
        widgets = {
            "last_seen": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
