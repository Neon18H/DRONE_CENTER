from django import forms
from fleet.models import Drone

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

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")
        pilot = cleaned_data.get("pilot")
        drone = cleaned_data.get("drone")

        if start_at and end_at and start_at >= end_at:
            self.add_error("end_at", "La hora de fin debe ser posterior al inicio.")

        if start_at and end_at and (pilot or drone):
            overlap_qs = Shift.objects.filter(start_at__lt=end_at, end_at__gt=start_at).exclude(
                status=Shift.Status.CANCELLED
            )
            if self.instance and self.instance.pk:
                overlap_qs = overlap_qs.exclude(pk=self.instance.pk)
            if pilot and overlap_qs.filter(pilot=pilot).exists():
                self.add_error("pilot", "El piloto ya tiene un turno en ese rango.")
            if drone and overlap_qs.filter(drone=drone).exists():
                self.add_error("drone", "El dron ya está asignado en ese rango.")
        return cleaned_data


class DispatchShiftForm(ShiftForm):
    class Meta(ShiftForm.Meta):
        fields = ["pilot", "drone", "route", "start_at", "end_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["drone"].queryset = self.fields["drone"].queryset.filter(status=Drone.Status.AVAILABLE)


class OperationSessionForm(forms.ModelForm):
    class Meta:
        model = OperationSession
        fields = ["notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
