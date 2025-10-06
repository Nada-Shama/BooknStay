from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.utils.crypto import get_random_string
from hotels.models import Hotel

# Create your views here.
def login_register(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    login_form = AuthenticationForm()
    # Keep a register_form in context for the existing template until fully migrated
    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect_user(user)
        elif 'register_submit' in request.POST:
            # Registration moved to separate page
            return redirect('register')

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

def contact(request):
    return render(request, 'users/contact.html')

'''
def hotels_search_results(request):
    return render(request, 'hotels/hotels-search-results.html')
'''

def login_view(request):
    # Keep /users/login/ working by redirecting to the unified auth page
    return redirect('login_register')

def register(request):
    if request.user.is_authenticated:
        return redirect_user(request.user)

    register_form = CustomUserCreationForm()
    if request.method == 'POST':
        register_form = CustomUserCreationForm(request.POST)
        if register_form.is_valid():
            saved_user = register_form.save()
            raw_password = register_form.cleaned_data.get('password1')
            auth_user = authenticate(request, username=saved_user.username, password=raw_password)
            if auth_user is not None:
                login(request, auth_user)
                return redirect_user(auth_user)
            login(request, saved_user, backend='users.backends.EmailOrUsernameBackend')
            return redirect_user(saved_user)

    return render(request, 'users/register.html', {
        'register_form': register_form,
    })

def logout_view(request):
    logout(request)
    return redirect('home')

'''
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
'''

def _is_owner_or_admin(user):
    return user.is_authenticated and (getattr(user, 'is_owner', lambda: False)() or user.is_staff or user.is_superuser)

# Owner Registration  
def owner_register(request):
    if request.method == 'POST':
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        phone = (request.POST.get('phone') or '').strip()
        password1 = (request.POST.get('password1') or '').strip()
        password2 = (request.POST.get('password2') or '').strip()

        hotel_name = (request.POST.get('hotel_name') or '').strip()
        property_type = (request.POST.get('property_type') or '').strip()
        star_rating = (request.POST.get('star_rating') or '').strip()
        address = (request.POST.get('address') or '').strip()
        zipcode = (request.POST.get('zipcode') or '').strip()
        city = (request.POST.get('city') or '').strip()
        state = (request.POST.get('state') or '').strip()
        country = (request.POST.get('country') or '').strip()
        amenities = request.POST.getlist('amenities')
        description = (request.POST.get('description') or '').strip()

        if not email or not hotel_name:
            messages.error(request, 'Email and Hotel Name are required.')
            return render(request, 'users/owner-register.html')

        if not password1 or not password2:
            messages.error(request, 'Password and confirmation are required.')
            return render(request, 'users/owner-register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/owner-register.html')

        # Create user if not exists
        User = get_user_model()
        existing = User.objects.filter(email=email).first()
        if existing:
            owner_user = existing
        else:
            # Generate a unique username from email local-part
            base_username = email.split('@')[0][:20] or 'owner'
            candidate = base_username
            idx = 1
            while User.objects.filter(username=candidate).exists():
                candidate = f"{base_username}{idx}"
                idx += 1
            owner_user = User.objects.create_user(
                username=candidate,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            # If custom user has phone field
            if hasattr(owner_user, 'phone') and phone:
                owner_user.phone = phone
                owner_user.save(update_fields=['phone'])

        # Ensure role is owner
        if hasattr(owner_user, 'role') and owner_user.role != 'owner':
            owner_user.role = 'owner'
            owner_user.save(update_fields=['role'])

        # Create hotel with minimal fields present in model
        location_parts = [p for p in [address, city, state, country] if p]
        location = ', '.join(location_parts) or city or country or 'Unknown'
        contact = phone or email
        amenities_text = ', '.join(amenities) if amenities else ''

        Hotel.objects.create(
            name=hotel_name,
            description=description or f"{property_type} • {star_rating}".strip(' •'),
            location=location,
            contact=contact,
            amenities=amenities_text,
        )

        messages.success(request, 'Thanks! Your owner account and hotel were submitted. You can log in and continue setup.')
        return render(request, 'users/login-register.html')

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

'''
def room_details(request, room_id):
    context = {
        'room_id': room_id,
    }
    return render(request, 'hotels/room-details.html', context)
'''

'''
@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_add_room(request):
    
    return render(request, 'hotels/owner-room-new.html')
'''