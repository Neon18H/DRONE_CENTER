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


class AlertAdminUpdateForm(forms.ModelForm):
    internal_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Agregar comentario interno"}),
        label="Comentario interno",
    )

    class Meta:
        model = Alert
        fields = ["assigned_to", "status"]
