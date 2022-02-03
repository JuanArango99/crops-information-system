from django.urls import path
from .views import (
    home_view, 
    ChartView,    
    csv_upload_view,
    uploadTemplateView,
    
    )

app_name = 'territorios'

urlpatterns = [
    path('', home_view, name='home'),
    path('charts/', ChartView.as_view(), name='charts'),
    path('from_file/', uploadTemplateView, name='from-file'),
    path('upload/', csv_upload_view, name='upload'),
    
]
