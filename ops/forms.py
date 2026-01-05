from django import forms

from .models import OperationSession, Route, Shift


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ["name", "zone_geojson", "waypoints", "risk_level"]
        widgets = {
            "zone_geojson": forms.Textarea(attrs={"rows": 4}),
            "waypoints": forms.Textarea(attrs={"rows": 4}),
        }


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["pilot", "drone", "route", "start_at", "end_at", "status"]
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class OperationSessionForm(forms.ModelForm):
    class Meta:
        model = OperationSession
        fields = ["notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
