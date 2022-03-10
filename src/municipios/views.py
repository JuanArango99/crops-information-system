from django.shortcuts import render
from .models import Municipio
from .forms import CreateMunicipio

def create_municipio_view(request):
    form = CreateMunicipio(request.POST or None)
    was_created = None
    alert_type = None
    message = None
    name = None
    if request.method == 'POST':
        name = request.POST.get('name').capitalize()        
        municipio_obj, created = Municipio.objects.get_or_create(name = name)
        if created:
            was_created = True
            alert_type = 'success'
            message = 'El municipio '+name+' fue creado satisfactoriamente'
        else:
            was_created = False
            alert_type = 'danger'
            message = '¡Ooopss..! Ya existe un municipio con el nombre de '+name

    context = {
        'form': form,
        'created': was_created,
        'alert_type': alert_type,
        'message': message,
        'name': name,
    }
    
    return render(request,'municipios/home.html', context)
