from urllib import request
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .forms import ChartForm, DatoForm, MunicipiosSearchForm, TerritoriesSearchForm, TerritorioForm
from .models import Dato, CSV
from territorios.models import Territorio
from municipios.models import Municipio
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.dateparse import parse_date
import csv
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def home_view(request):
    form = TerritoriesSearchForm(request.POST or None)
    no_data = None
    obj = None
    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')        
        id_territorio = request.POST.get('territorio')
        territorio = Territorio.objects.get(id=id_territorio)    
                
        obj = Dato.objects.filter(
                territorio=territorio,
                year__lte=date_to,
                year__gte = date_from                
                )
        if len(obj) == 0:
            no_data = 'No se encontraron registros en las fechas seleccionadas'

    context = {
        'form': form,
        'obj': obj,   
        'no_data': no_data,

    }

    return render(request,'territorios/home.html', context)

def chartView(request):
    #form = ChartForm(request.POST or None)
    territorioForm = TerritorioForm()
    datoForm = DatoForm()
    qs =  None
    if request.method == 'POST':
        municipio = request.POST.get('municipio')
        territorio = request.POST.get('territorio')

        qs = Dato.objects.filter(territorio = territorio)
    context = {
        'qs': qs,
        'territorioForm':territorioForm,
        'datoForm':datoForm,
    }

    return render(request, 'territorios/charts.html', context)

def load_territorios(request):
    municipio_id = request.GET.get('municipio')
    if municipio_id != '':        
        territorios = Territorio.objects.filter(municipio=municipio_id).order_by('name')    
    else:
        territorios = Territorio.objects.none()
        
    return render(request, 'territorios/prueba.html', {'territorios': territorios}) 

@login_required
def uploadTemplateView(request):
    form = MunicipiosSearchForm(request.POST or None)
    if request.method == 'POST':
        municipio = request.POST.get('municipio')        
      
    context = {
        'form': form,
    }

    return render(request,'territorios/from_file.html', context)

@login_required
def csv_upload_view(request):
    
    if request.method == 'POST':
        id_municipio = request.POST.get('municipio')        
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj, created = CSV.objects.get_or_create(file_name = csv_file_name)
        if created:
            obj.csv_file = csv_file
            obj.save() 
            #Leer dataset
            # - - - - - - - REMOVER NROWS DE DATAFRAME 'DATA' - - - - - - - 
            data = pd.read_csv(obj.csv_file.path,skiprows=12, nrows=2,dtype={'DOY': object,'YEAR': object})
            data['DATE'] = pd.to_datetime(data['YEAR']+"-"+data['DOY'], format='%Y-%j').dt.strftime('%d-%m-%Y')
            data['DATE'] = pd.to_datetime(data['DATE'],format='%d-%m-%Y')
            #Obtener Longitud y Latitud apartir del csv
            data_position = pd.read_csv(obj.csv_file.path,skiprows = 3, nrows=0)
            nombre_territorio = csv_file_name.split(".")[0]
            nombre_territorio = nombre_territorio.replace("_"," ")       
            for i in data_position.columns:
                a = i
            longitud = float(a.split()[2])
            latitud = float(a.split()[4])            
            #Crear objeto territorio
            municipio = Municipio.objects.get(id=id_municipio)
            territorio_obj = Territorio.objects.create(
                name = nombre_territorio,
                longitud = longitud,
                latitud = latitud,
                municipio = municipio
            )
            territorio_obj.save()
            territorio = Territorio.objects.get(id=territorio_obj.pk)                            
            
            for i in range(data.shape[0]):
                year = data['DATE'][i]
                irradiance = data['ALLSKY_SFC_SW_DWN'][i]
                temperature = data['T2M'][i]
                relative_humidity=data['RH2M'][i]
                precipitation = data['PRECTOTCORR'][i]                

                data_obj = Dato.objects.create(
                    year=year,
                    irradiance=irradiance,
                    temperature=temperature,
                    relative_humidity=relative_humidity,
                    precipitation=precipitation,
                    territorio=territorio                    
                    )
                data_obj.save()
            return JsonResponse({'created': True})
        return JsonResponse({'created': False})
    return HttpResponse()


def render_pdf_view(request, pk):
    template_path = 'territorios/pdf.html'
    obj = get_object_or_404(Dato, pk=pk)
    context = {'obj': obj}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    #if download
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #if display in browser
    response['Content-Disposition'] = 'filename="data.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
