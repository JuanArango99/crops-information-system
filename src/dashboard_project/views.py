from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def home_view(request):

    return render(request,'home.html')

def news_view(request):
    return render(request,'news.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def login_view(request):
    error_message = None
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if username is not None:
                login(request, user)
                if request.GET.get('next'):
                    return redirect(request.GET.get('next'))
                else: #Return to home
                    return redirect('home')
        else:
            error_message = 'Lo sentimos.. Algo ocurrió mal'
    
    context = {
        'form': form,
        'error_message': error_message
    }

    return render(request, 'auth/login.html', context)
