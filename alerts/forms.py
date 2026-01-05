from django import forms

from .models import Alert


class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = [
            "category",
            "severity",
            "target",
            "location_lat",
            "location_lng",
            "description",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
