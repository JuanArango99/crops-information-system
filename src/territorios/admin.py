from django.contrib import admin
from .models import Territorio, Dato, CSV
# Register your models here.
admin.site.register(Territorio)
admin.site.register(Dato)
admin.site.register(CSV)