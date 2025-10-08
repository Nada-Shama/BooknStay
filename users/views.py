from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from .forms import ProfileUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.utils.crypto import get_random_string
from hotels.models import Hotel, Room
from bookings.models import Booking
from django.views.decorators.http import require_POST
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.http import JsonResponse
from datetime import date

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

    return render(request, 'users/login.html', {
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

        # Create hotel using valid fields on the Hotel model and set owner
        try:
            star_rating_int = int(star_rating) if star_rating else None
        except ValueError:
            star_rating_int = None

        Hotel.objects.create(
            owner=owner_user,
            hotel_name=hotel_name,
            property_type=property_type or None,
            star_rating=star_rating_int,
            address=address or None,
            zipcode=zipcode or None,
            city=city or None,
            state=state or None,
            country=country or None,
            amenities=amenities or [],
            description=description or '',
            contact_preference='Email' if email else 'Phone',
            business_name=None,
            tax_id=None,
            website=None,
        )

        messages.success(request, 'Thanks! Your owner account and hotel were submitted. You can log in and continue setup.')
        return render(request, 'users/login.html')

    return render(request, 'users/owner-register.html')

@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_dashboard(request):
    # Recent bookings for hotels owned by this user
    recent_bookings = Booking.objects.filter(hotel__owner=request.user).select_related('hotel', 'room', 'user')[:10]
    return render(request, 'users/owner-dashboard.html', {
        'recent_bookings': recent_bookings,
    })

@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_bookings_calendar_data(request):

    # Placeholder: mock reservation counts per day for current month (1..31)



    # TODO: Replace with real Booking aggregation per date for this owner
    # Example mocked data
    sample = {1: 2, 3: 4, 5: 1, 7: 6, 9: 3, 12: 5, 15: 2, 18: 8, 20: 4, 22: 1, 24: 2, 27: 3, 30: 7, 31:12}

    def color_for(count: int) -> str:
        if count >= 10:
            return '#e74c3c'  # red (busy)
        if count >= 5:
            return '#f39c12'  # yellow (medium)
        return '#2ecc71'      # green (light)

    today = date.today()
    events = []
    for d, c in sample.items():
        events.append({
            'title': f'{c} bookings',
            'start': f'{today.year}-{today.month:02d}-{d:02d}',
            'color': color_for(c),
            'allDay': True,
        })
    return JsonResponse(events, safe=False)

@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_hotels(request):
    hotels = Hotel.objects.filter(owner=request.user).order_by('-created_at')
    context = {
        'hotels': hotels,
    }
    return render(request, 'users/owner-hotels.html', context)


@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_bookings(request):
    bookings = Booking.objects.filter(hotel__owner=request.user).select_related('hotel', 'room', 'user').order_by('-created_at')
    return render(request, 'users/owner-bookings.html', {
        'bookings': bookings,
    })

@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_profile(request):
    user = request.user
    if request.method == 'POST':
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        phone = (request.POST.get('phone') or '').strip()
        date_of_birth = (request.POST.get('date_of_birth') or '').strip()
        nationality = (request.POST.get('nationality') or '').strip()
        bio = (request.POST.get('bio') or '').strip()

        # Basic updates with minimal validation
        # Ensure username uniqueness if changed
        if username and username != user.username:
            UserModel = get_user_model()
            if UserModel.objects.filter(username=username).exclude(pk=user.pk).exists():
                messages.error(request, 'Username is already taken.')
            else:
                user.username = username

        # Ensure email uniqueness if changed
        if email and email != user.email:
            UserModel = get_user_model()
            if UserModel.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, 'Email is already in use by another account.')
            else:
                user.email = email

        user.first_name = first_name
        user.last_name = last_name
        if hasattr(user, 'phone'):
            user.phone = phone
        if hasattr(user, 'nationality'):
            user.nationality = nationality
        if hasattr(user, 'date_of_birth'):
            # Accept YYYY-MM-DD
            user.date_of_birth = date_of_birth or None

        user.save()
        messages.success(request, 'Profile updated successfully.')

        # Note: bio/avatar placeholders for future profile model

    context = {
        'profile': {
            'first_name': getattr(user, 'first_name', ''),
            'last_name': getattr(user, 'last_name', ''),
            'username': getattr(user, 'username', ''),
            'email': getattr(user, 'email', ''),
            'phone': getattr(user, 'phone', ''),
            'date_of_birth': getattr(user, 'date_of_birth', None),
            'nationality': getattr(user, 'nationality', ''),
            'bio': '',
            'avatar_url': '',
        }
    }
    return render(request, 'users/owner-profile.html', context)

@login_required(login_url='login_register')
def account(request):
    user_bookings = []
    if request.user.is_authenticated:
        user_bookings = Booking.objects.filter(user=request.user).select_related('hotel', 'room').order_by('-created_at')

    # Forms for profile and password on the same page
    pwd_form_cls = SetPasswordForm if not request.user.is_authenticated or not request.user.has_usable_password() else PasswordChangeForm
    pwd_form = None
    profile_form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'profile':
                profile_form = ProfileUpdateForm(request.POST, instance=request.user)
                if profile_form.is_valid():
                    profile_form.save()
                    messages.success(request, 'Profile updated successfully.')
                    return redirect('account')
            elif action == 'password':
                pwd_form = pwd_form_cls(request.user, request.POST)
                if pwd_form.is_valid():
                    pwd_form.save()
                    messages.success(request, 'Password updated successfully.')
                    return redirect('account')
                # Remove autofocus that can auto-scroll on invalid submit
                for f in pwd_form.fields.values():
                    f.widget.attrs.pop('autofocus', None)
        # GET or invalid POST
        profile_form = profile_form or ProfileUpdateForm(instance=request.user)
        pwd_form = pwd_form or pwd_form_cls(request.user)
        # Remove autofocus to avoid page auto-scrolling to password
        if pwd_form:
            for f in pwd_form.fields.values():
                f.widget.attrs.pop('autofocus', None)

    context = {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
        'bookings': user_bookings,
        'profile_form': profile_form,
        'pwd_form': pwd_form,
    }
    return render(request, 'users/account.html', context)


@login_required(login_url='login_register')
def add_favorite_room(request, room_id):
    from users.models import FavoriteRoom
    room = get_object_or_404(Room, id=room_id)
    FavoriteRoom.objects.get_or_create(user=request.user, room=room)
    messages.success(request, 'Added to favorites.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'list_favorites'
    return redirect(next_url)


@login_required(login_url='login_register')
def remove_favorite_room(request, room_id):
    from users.models import FavoriteRoom
    room = get_object_or_404(Room, id=room_id)
    FavoriteRoom.objects.filter(user=request.user, room=room).delete()
    messages.success(request, 'Removed from favorites.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'list_favorites'
    return redirect(next_url)


@login_required(login_url='login_register')
def list_favorites(request):
    from users.models import FavoriteRoom
    items = FavoriteRoom.objects.filter(user=request.user).select_related('room', 'room__hotel')
    return render(request, 'users/favorites.html', {'items': items})


@login_required(login_url='login_register')
def settings_view(request):
    # Alias settings to account page; surface password-setup prompt via message
    if request.session.pop('needs_password_setup', False):
        messages.info(request, 'Welcome! Please set your password below.')
    return redirect('account')


@require_POST
def validate_password_ajax(request):
    """Validate password against Django validators and return messages."""
    password = (request.POST.get('password') or '').strip()
    try:
        validate_password(password, user=request.user if request.user.is_authenticated else None)
        return JsonResponse({'valid': True, 'errors': []})
    except ValidationError as ve:
        return JsonResponse({'valid': False, 'errors': list(ve.messages)})


