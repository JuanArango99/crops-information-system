from django.urls import path
from .views import (
    reports_view, 
    chartView,
    statisticView,
    csv_upload_view,
    mapView,
    uploadTemplateView,
    load_territorios,

    )

app_name = 'territorios'

urlpatterns = [
    path('reports/', reports_view, name='reports'),
    path('charts/', chartView, name='charts'),
    path('statistics/', statisticView, name='statistics'),
    path('from_file/', uploadTemplateView, name='from-file'),
    path('upload/', csv_upload_view, name='upload'),
    path('map/', mapView, name='map'),
    path('ajax/load-cities/', load_territorios, name='ajax_load_cities'),  # <-- this one here
   
]
