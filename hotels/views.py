from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room, Review,RoomImage
from django.db.models import Avg
from django.contrib import messages
from users.models import User
from users.views import _is_owner_or_admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import traceback
from .forms import RoomForm,HotelForm

def home(request):
    hotels = Hotel.objects.all()
    return render(request, 'users/home.html', {'hotels': hotels})


def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotels/hotels.html', {'hotels': hotels})



def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.all()
    reviews = hotel.reviews.all().order_by('-created_at')
    user_has_review = False
    if request.user.is_authenticated:
        user_has_review = reviews.filter(user=request.user).exists()

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'reviews': reviews,
        'user_has_review': user_has_review,
    }
    return render(request, 'hotels/property-details.html', context)

@require_POST
@login_required
def add_review(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rating_str = request.POST.get('rating')
    comment = (request.POST.get('comment') or '').strip()

    try:
        rating = int(rating_str)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid rating value.'})

    if not (1 <= rating <= 5):
        return JsonResponse({'success': False, 'error': 'Rating must be between 1 and 5.'})

    # Enforce one review per user per hotel (atomic)
    review, created = Review.objects.get_or_create(
        user=request.user,
        hotel=hotel,
        defaults={
            'rating': rating,
            'comment': comment,
            'review_date': timezone.now().date(),
        }
    )
    if not created:
        return JsonResponse({'success': False, 'error': 'You have already reviewed this hotel.'})

    return JsonResponse({
        'success': True,
        'username': request.user.username,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at.strftime("%b %d, %Y"),
    })




def book_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel, status='available')
    context = {'hotel': hotel, 'rooms': rooms}
    return render(request, 'bookings/booking.html', context)


    # Note: duplicate add_review definition removed; using the login-required JSON endpoint above.

def owner_register(request):
    return render(request, 'users/owner-register.html')

def properties(request):
    return render(request, 'hotels/new-hotel.html')



def all_hotels(request):
    return render(request, 'hotels/all-hotels.html')

def all_rooms(request):
    rooms = Room.objects.select_related('hotel').prefetch_related('images').order_by('-created_at')
    return render(request, 'hotels/all-rooms.html', { 'rooms': rooms })



def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'hotels/room-details.html', {'room': room})



@login_required(login_url='login_register')
@user_passes_test(_is_owner_or_admin, login_url='login_register')
def owner_add_room(request):
    
    return render(request, 'hotels/owner-room-new.html')



@login_required
def new_hotel(request):
    amenities_list = ['Free Wi‑Fi', 'Parking', 'Pool', 'Spa', 'Gym', 'Restaurant', 'Pet Friendly', 'Airport Shuttle']
    property_types = ['Hotel', 'Resort', 'Boutique Hotel', 'Guest House', 'Apartment']
    star_ratings = ['1 Star', '2 Stars', '3 Stars', '4 Stars', '5 Stars']
    contact_methods = ['Email', 'Phone']

    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            form.save_m2m()

            messages.success(request, "Hotel has been added successfully!")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HotelForm()

    context = {
        'form': form,
        'amenities_list': amenities_list,
        'property_types': property_types,
        'star_ratings': star_ratings,
        'contact_methods': contact_methods
    }
    return render(request, 'hotels/new-hotel.html', context)


@login_required
def owner_add_room(request):
    owner_hotels = Hotel.objects.filter(owner=request.user)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        hotel_id = request.POST.get('assign_hotel')
        hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)

        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()

            for f in request.FILES.getlist('images'):
                RoomImage.objects.create(room=room, image=f)

            messages.success(request, "Room added successfully!")
            return redirect('owner_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RoomForm()

    return render(request, 'hotels/owner-room-new.html', {'form': form, 'owner_hotels': owner_hotels})
