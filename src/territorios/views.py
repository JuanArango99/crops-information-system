
from calendar import month
from tkinter.messagebox import NO
from urllib import response
from django import template
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import numpy as np
from .forms import ChartForm, DatoForm, MunicipiosSearchForm, TerritoriesSearchForm, TerritorioForm, StatisticForm
from .models import Dato, CSV
from territorios.models import Territorio
from municipios.models import Municipio
from django.http import JsonResponse
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from django.contrib.auth.decorators import login_required
import folium
from branca.element import Figure
from django.core.paginator import Paginator
from datetime import datetime
import csv
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Count

register = template.Library()
@register.filter
def get_attr(object, name):
    return getattr(object, name, '')

def reports_view(request):
    form = TerritoriesSearchForm(request.POST or None)
    no_data = None
    obj = None
    datos=None
    territorio=None
    date_from=None
    date_to=None
    objs = []
                
    if request.method == 'POST':
        if form.is_valid():
            date_from = request.POST.get('date_from')
            date_to = request.POST.get('date_to')        
            id_territorio = request.POST.get('territorio')
            territorio = Territorio.objects.get(id=id_territorio)                 
            objs = Dato.objects.filter(
                    territorio=territorio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )
            obj = objs[:10]                
            request.session['territorio'] = id_territorio
            request.session['date_to'] = date_to
            request.session['date_from'] = date_from
            if len(obj) == 0:
                no_data = 'No se encontraron registros en las fechas seleccionadas.'
        p = Paginator(obj,10)        
        page = request.GET.get('page')
        datos = p.get_page(page)
        

    context = {
        'form': form,
        'obj': obj,  
        'cantidad':len(objs),
        'date_from':date_from,
        'date_to':date_to,
        'territorio':territorio, 
        'datos': datos,
        'no_data': no_data,
    }
    return render(request,'territorios/reports.html', context)

def export(request):
    id_territorio=request.session['territorio'] 
    territorio = Territorio.objects.get(id=id_territorio)                        
    date_to=request.session['date_to'] 
    date_from=request.session['date_from'] 
    obj = Dato.objects.filter(
                    territorio=territorio,
                    year__lte=date_to,
                    year__gte = date_from                
                    )    
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Fecha','Radiacion Solar', 'Temperatura','Humedad Relativa','Precipitacion'])
    for dato in obj.values_list('year','irradiance','temperature','relative_humidity', 'precipitation'):
        writer.writerow(dato)

    response['Content-Disposition']='attachment;filename=Reporte '+territorio.name+' ('+date_from+' - '+date_to+') '+'.csv'

    return response

def mapView(request):
    #Son 19 colores disponibles por folium para el color de icono.
    colors = ['red', 'orange', 'green', 'darkblue', 'darkgreen', 'black', 'darkred', 'cadetblue', 'pink', 'lightblue', 'purple', 'beige', 'gray', 'lightgray', 'blue', 'darkpurple', 'lightred', 'lightgreen', 'white']
    #Coordenadas para centrar el mapa en cesar
    lon = 9.129754392830863
    lat = -73.53600433475354
    territorios = Territorio.objects.all()   
    municipios = Municipio.objects.all()
    municipiosPk = [] # Lista de las PK de los municipios
    municipiosName= [] # Lista de los nombres de los municipios
    for municipio in municipios:
        municipiosPk.append(municipio.pk)
        municipiosName.append(municipio.name)    
    municipiosColorName = {}
    municipiosColor = {} # Diccionario con los colores de cada municipio. 
                        #La PK del Municipio es la key y el value es un color de la lista de colores 'colors'
    for i in range(len(municipiosPk)):
        municipiosColorName[municipiosName[i]] = colors[i]
        municipiosColor[municipiosPk[i]] = colors[i]   # Ej: diccionario<key=municipioPk, value=color
                                                      #  {'1':'red; '2':orange'  ....}
    fig = Figure(width="100%", height="550px")
    m = folium.Map(
        location=[lon,lat],
        tiles="OpenStreetMap",        
        width="100",
        height="100",
        zoom_start=8)    
    
    folium.TileLayer(name="Relieve",
    tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', 
    attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)').add_to(m)        
    folium.TileLayer(name="Satelital",
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
    attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community').add_to(m)    
    folium.LayerControl().add_to(m)
    fig.add_child(m)
    folium.LatLngPopup().add_to(m)

    for item in territorios:
        folium.CircleMarker(location=(item.longitud,item.latitud),radius=10, fill_color='green').add_to(m)
        folium.Marker(
            location=(item.longitud,item.latitud),popup=item.name,tooltip=item.name, 
            icon=folium.Icon(color=municipiosColor[item.municipio.pk], icon_color='#ffffff')).add_to(m)
        folium.map.Layer()

    m = m._repr_html_()
    context={
        'map':m,
        'municipios': municipiosColorName, 
    }
    return render(request,'territorios/mapa.html',context)

def statisticView(request):
    form = StatisticForm()
    territorioForm = TerritorioForm()
    datoForm = DatoForm()
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')  
    variableX = None
    variableY = None
    dataX = []
    dataY = []
    qs=None
    data=None

    if request.method == 'POST':
        variableX=request.POST.get('variableX')
        variableY=request.POST.get('variableY')
        territorio = request.POST.get('territorio')

        qs = Dato.objects.filter(
            territorio = territorio,
            year__lte=date_to,
            year__gte = date_from  
        )
        for item in qs:
            dataX.append(getattr(item, variableX))
            dataY.append(getattr(item, variableY))      

    context = {
        'qs': qs,
        'territorioForm':territorioForm,
        'datoForm':datoForm,
        'form':form,
        'variableX':variableX,
        'variableY':variableY,
        'data':data,    
        'dataX': dataX,    
        'dataY': dataY,    
    }
    return render(request, 'territorios/statistics.html', context)

def chartView(request):
    unidadesDict = {'temperature': '°C', 'relative_humidity': "%", 'irradiance': "MJ/m^2", 'precipitation': "mm"}
    territorioForm = TerritorioForm()
    datoForm = DatoForm(request.POST or None)
    form = ChartForm(request.POST or None)
    date_from = request.POST.get('date_from')
    date_to = request.POST.get('date_to')   
    qs =  None
    variable = None    
    data = []
    territorio = None
    territorioObj = None
    unidades=None
    df=None
    dati=None
    datos=None
    fechas=None
    fechas=[]
    promedio = 0
    minimo = 0
    maximo = 0
    variableName=None
    if request.method == 'POST':
        if form.is_valid():
            territorio = request.POST.get('territorio')
            variable = str(request.POST.get('variable'))
            variableName = form.cleaned_data['variable']
            variableName = dict(form.fields['variable'].choices)[variableName]            
            territorioObj = Territorio.objects.get(id=territorio)                 
            qs = Dato.objects.filter(
                territorio = territorio,
                year__lte=date_to,
                year__gte = date_from  
            )
            df = pd.DataFrame(list(qs.values('year', variable)))
            dati=df.groupby(pd.PeriodIndex(df['year'], freq="M"))[variable].mean().reset_index()
            datos = [i for i in dati[variable].values]
            promedio = np.average(datos)
            minimo = np.min(datos)
            maximo = np.max(datos)
            fechas = dati['year']    
            for item in qs:
                data.append(getattr(item, variable))
            unidades = unidadesDict[variable]            
        
    context = {
        'qs': qs,
        'territorioObj': territorioObj,
        'territorioForm':territorioForm,
        'datoForm':datoForm,
        'form':form,
        'variable':variable,
        'variableName':variableName,
        'data':data,        
        'fechas':fechas,
        'datos':datos,
        'promedio': round(promedio,2),
        'minimo':round(minimo,2),
        'maximo':round(maximo,2),
        'unidades':unidades,


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
            data = pd.read_csv(obj.csv_file.path,skiprows=12, dtype={'DOY': object,'YEAR': object})
            data = data.replace(-999.0, np.NaN)
            data = data.fillna(method='bfill')
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
                municipio = municipio)
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



def export_csv(request):

    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment;filename=Reportes'+ \
        datetime.datetime.now()+'.csv'

    writer=csv.writer(response)
    writer.writerow(['Fecha','Radiacion Solar', 'Temperatura','Precipitación','Humedad Relativa'])



def render_pdf_view(request):
    template_path = 'territorios/pdf.html'
    context = {'myvar': 'this is your template context'}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # if download
    #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    #if display in browser
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
