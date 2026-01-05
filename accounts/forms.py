from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class PilotCreateForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    full_name = forms.CharField(max_length=150, required=True)
    photo = forms.ImageField(required=False)
    phone = forms.CharField(max_length=30, required=False)
    badge_id = forms.CharField(max_length=50, required=False)
    station = forms.CharField(max_length=100, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username


class PilotUpdateForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    full_name = forms.CharField(max_length=150, required=True)
    photo = forms.ImageField(required=False)
    phone = forms.CharField(max_length=30, required=False)
    badge_id = forms.CharField(max_length=50, required=False)
    station = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)
        if self.user_instance:
            qs = qs.exclude(pk=self.user_instance.pk)
        if qs.exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username
