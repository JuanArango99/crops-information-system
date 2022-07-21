from django import forms

from municipios.models import Municipio

class CreateMunicipio(forms.Form):
    name = forms.CharField(max_length=20)

class MunicipiosSearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))    
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())