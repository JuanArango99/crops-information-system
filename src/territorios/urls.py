from django.urls import path
from .views import (
    home_view, 
    chartView,
    csv_upload_view,
    mapView,
    uploadTemplateView,
    load_territorios,

    )

app_name = 'territorios'

urlpatterns = [
    path('', home_view, name='home'),
    path('charts/', chartView, name='charts'),
    path('from_file/', uploadTemplateView, name='from-file'),
    path('upload/', csv_upload_view, name='upload'),
    path('map/', mapView, name='map'),
    path('ajax/load-cities/', load_territorios, name='ajax_load_cities'),  # <-- this one here
   
]
