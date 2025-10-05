from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

# Create your views here.
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

def properties(request):
    return render(request, 'properties.html')

def property_details(request):
    return render(request, 'property-details.html')

def contact(request):
    return render(request, 'contact.html')

def hotels(request):
    return render(request, 'hotels.html')

def login_view(request):
    form = AuthenticationForm()
    return render(request, 'users/login-register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def booking(request):
    """Handle hotel booking page for both guests and authenticated users"""
    context = {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
    }
    
    # If user is authenticated, pre-fill some form data
    if request.user.is_authenticated:
        context.update({
            'user_email': request.user.email,
            'user_first_name': request.user.first_name,
            'user_last_name': request.user.last_name,
        })
    
    return render(request, 'booking.html', context)

def owner_register(request):
    return render(request, 'owner-register.html')