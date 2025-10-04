from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

# Create your views here.
'''
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after register
            return redirect_user(user)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/login-register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect_user(user)
    else:
        form = AuthenticationForm()
    return render(request, 'users/login-register.html', {'form': form})
'''

def login_register(request):
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        if 'login_submit' in request.POST:  # user clicked login form
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect_user(user)

        elif 'register_submit' in request.POST:  # user clicked register form
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect_user(user)

    return render(request, 'users/login-register.html', {
        'login_form': login_form,
        'register_form': register_form,
    })

def redirect_user(user):
    """Redirect based on role"""
    if user.is_customer():
        return redirect('home')  # customers → homepage
    elif user.is_owner():
        return redirect('owner_dashboard')  # owners → dashboard
    elif user.is_superuser or user.is_admin():
        return redirect('/admin/')  # admins → Django Admin
    return redirect('home')

def home(request):
    return render(request, 'home.html')
