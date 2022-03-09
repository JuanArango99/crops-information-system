from attr import fields
from django import forms
from municipios.models import Municipio
from territorios.models import Dato, Territorio

class TerritoriesSearchForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))    
    territorio = forms.ModelChoiceField(queryset=Territorio.objects.all())

class MunicipiosSearchForm(forms.Form):
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())

class ChartForm(forms.Form):
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))    
    municipio = forms.ModelChoiceField(queryset=Municipio.objects.all())
    territorio = forms.ModelChoiceField(queryset=Territorio.objects.all())
    
class TerritorioForm(forms.ModelForm):
    class Meta:
        model = Territorio
        fields = ('municipio',)

class DatoForm(forms.ModelForm):
    class Meta:
        model = Dato
        fields = ('territorio',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['territorio'].queryset = Territorio.objects.none()


       
            

