from django import forms
from django.core.validators import RegexValidator


class CreateMunicipio(forms.Form):
    name = forms.CharField(
        max_length=255,
    )

