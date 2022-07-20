from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import CSV, Dato, Municipio
from .forms import CreateMunicipio
from django.contrib.auth.decorators import login_required
import pandas as pd
import numpy as np



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
            nombres = ['Municipio','Year','Periodo','Area Sembrada', 'Area Cosechada', 'Produccion','Rendimiento']
            for i in range(len(nombres)):
                data.columns.values[i] = nombres[i]
            Munis = ["Aguachica","Agustin Codazzi","Bosconia","La Paz","Rio De Oro","San Alberto","San Diego","San Martin","Valledupar"]
            Munis = [x.upper() for x in Munis]
            data = data[data['Municipio'].isin(Munis)]
            data = data.groupby(['Municipio','Year','Periodo']).sum().reset_index()
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
                area_sembrada = data['Area Sembrada'][i]
                area_cosechada = data['Area Cosechada'][i]
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
