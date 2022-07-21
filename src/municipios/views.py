from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import CSV, Dato, Municipio
from .forms import MunicipiosSearchForm
from django.contrib.auth.decorators import login_required
import pandas as pd
from django.core.paginator import Paginator
import csv


def reports_view(request):
    form = MunicipiosSearchForm(request.POST or None)
    no_data = None
    obj = None
    datos=None
    municipio=None
    date_from=None
    date_to=None
    objs = []

    if request.method == 'POST':
        if form.is_valid():
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')
            id_municipio = request.POST.get('municipio')
            municipio = Municipio.objects.get(id=id_municipio)   
            objs = Dato.objects.filter(
                    municipio=municipio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )  
            obj = objs[:5]                
            request.session['municipio'] = id_municipio
            request.session['date_to'] = date_to
            request.session['date_from'] = date_from
            if len(obj) == 0:
                no_data = 'No se encontraron registros en las fechas seleccionadas.'
        p = Paginator(obj,5)        
        page = request.GET.get('page')
        datos = p.get_page(page) 

    context={
        'form': form,
        'obj': obj,  
        'cantidad':len(objs),
        'date_from':date_from,
        'date_to':date_to,
        'municipio':municipio, 
        'datos': datos,
        'no_data': no_data,
    }
    return render(request,'municipios/reports.html', context)

def export(request):
    id_municipio=request.session['municipio'] 
    municipio = Municipio.objects.get(id=id_municipio)                        
    date_to=request.session['date_to'] 
    date_from=request.session['date_from'] 
    obj = Dato.objects.filter(
                    municipio=municipio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )  
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Año','Periodo', 'Area Sembrada','Area Cosechada','Produccion','Rendimiento'])
    for dato in obj.values_list('year','period','area_sembrada','area_cosechada','produccion','rendimiento'):
        writer.writerow(dato)

    response['Content-Disposition']='attachment;filename=Reporte '+municipio.name+' ('+date_from+' - '+date_to+') '+'.csv'

    return response

@login_required
def create_municipio_view(request):
    context = {}
    return render(request,'municipios/home.html', context)

@login_required
def csv_upload_view(request):
    if request.method == 'POST':
        csv_file_name = request.FILES.get('file').name
        csv_file = request.FILES.get('file')
        obj, created = CSV.objects.get_or_create(file_name = csv_file_name)
        if created:
            obj.csv_file = csv_file
            obj.save()
            #Leer dataset            
            df = pd.read_csv(obj.csv_file.path, parse_dates=['AÑO'])
            data = df.iloc[:,[3,8,9,10,11,12,13]]
            nombres = ['Municipio','Year','Periodo','Area_Sembrada', 'Area_Cosechada', 'Produccion','Rendimiento']
            for i in range(len(nombres)):
                data.columns.values[i] = nombres[i]
            Munis = ["Aguachica","Agustin Codazzi","Bosconia","La Paz","Rio De Oro","San Alberto","San Diego","San Martin","Valledupar"]
            Munis = [x.upper() for x in Munis]
            data = data[data['Municipio'].isin(Munis)]
            data=data.groupby(['Municipio','Year','Periodo']).sum().reset_index()
            data=data.sort_values(by=['Municipio','Year'])            
            data['Rendimiento'] = data.apply(lambda row: row.Produccion / row.Area_Cosechada if row.Area_Cosechada > 0 else 0 , axis=1)
            data = data.reset_index(drop=True)            
            #Crear obj municipio
            for muni in Munis:
                municipio_obj, createdd = Municipio.objects.get_or_create(name=muni)
                if createdd:
                    municipio_obj.save()       
            #Crear obj dato
            for i in range(data.shape[0]):
                year = data['Year'][i]
                period = data['Periodo'][i]
                area_sembrada = data['Area_Sembrada'][i]
                area_cosechada = data['Area_Cosechada'][i]
                produccion = data['Produccion'][i]
                rendimiento = data['Rendimiento'][i]
                municipio = Municipio.objects.get(name=data['Municipio'][i])

                data_obj = Dato.objects.create(
                    year=year,
                    period=period,
                    area_sembrada=area_sembrada,
                    area_cosechada=area_cosechada,
                    produccion=produccion,
                    rendimiento=rendimiento,
                    municipio=municipio
                    )
                data_obj.save()
            return JsonResponse({'created':True})
        return JsonResponse({'created':False,'fileName':csv_file_name})
    return HttpResponse()
