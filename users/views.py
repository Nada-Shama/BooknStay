from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

# Create your views here.
def login_register(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

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
                saved_user = register_form.save()
                raw_password = register_form.cleaned_data.get('password1')
                # Authenticate to attach the backend; prefer username to avoid email uniqueness ambiguity
                auth_user = authenticate(request, username=saved_user.username, password=raw_password)
                if auth_user is not None:
                    login(request, auth_user)
                    return redirect_user(auth_user)
                # Fallback: explicitly specify backend if authenticate did not return a user
                login(request, saved_user, backend='users.backends.EmailOrUsernameBackend')
                return redirect_user(saved_user)

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
    return render(request, 'users/home.html')

def properties(request):
    return render(request, 'hotels/properties.html')

def property_details(request):
    return render(request, 'hotels/property-details.html')

def contact(request):
    return render(request, 'users/contact.html')

def hotels_search_results(request):
    return render(request, 'hotels/hotels-search-results.html')

def all_hotels(request):
    return render(request, 'hotels/all-hotels.html')

def login_view(request):
    # Keep /users/login/ working by redirecting to the unified auth page
    return redirect('login_register')

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

    return render(request, 'bookings/booking.html', context)

def _is_owner_or_admin(user):
    return user.is_authenticated and (getattr(user, 'is_owner', lambda: False)() or user.is_staff or user.is_superuser)

# Owner Registration page for new owners 
@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_register(request):
    if request.method == 'POST':
        # Lightweight validation: enforce email matches authenticated account
        posted_email = (request.POST.get('email') or '').strip()
        if posted_email and posted_email.lower() != (request.user.email or '').lower():
            messages.error(request, 'Please use the same email address associated with your account.')
            return render(request, 'users/owner-register.html')
        messages.success(request, 'Your registration request has been received.')
        return render(request, 'users/owner-register.html')
    return render(request, 'users/owner-register.html')

@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_dashboard(request):
    return render(request, 'users/owner-dashboard.html')

@login_required(login_url='login_register')
def account(request):
    return render(request, 'users/account.html', {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
    })

@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_add_room(request):
    return render(request, 'hotels/owner-room-new.html')

def room_details(request, room_id):
    context = {
        'room_id': room_id,
    }
    return render(request, 'hotels/room-details.html', context)