from django import forms
from municipios.models import Municipio
from territorios.models import Territorio

CHART_CHOICES = (
    ('#1', 'Bar chart'),
    ('#2', 'Pie chart'),
    ('#3', 'Line chart'),
)


class TerritoriesSearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    chart_type = forms.ChoiceField(choices=CHART_CHOICES)
    territorio = forms.ModelChoiceField(queryset=Territorio.objects.all())

class MunicipiosSearchForm(forms.Form):
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())

    

