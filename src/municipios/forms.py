from django import forms

class CreateMunicipio(forms.Form):
    name = forms.CharField(max_length=20)

