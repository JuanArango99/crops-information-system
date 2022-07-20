from xml.etree.ElementInclude import include
from django.urls import path
from .views import create_municipio_view,csv_upload_view

app_name = 'municipios'

urlpatterns = [
 path('', create_municipio_view, name = "home"),   
 path('upload/', csv_upload_view, name='upload'),

]
