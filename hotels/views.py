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

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'reviews': reviews,
    }
    return render(request, 'hotels/property-details.html', context)

@require_POST
@login_required
def add_review(request, hotel_id):
    try:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()

        if not (1 <= rating <= 5):
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'})

        review = Review.objects.create(
            hotel=hotel,
            user=request.user,
            rating=rating,
            comment=comment
        )

        return JsonResponse({
            'success': True,
            'username': request.user.username,
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.strftime("%b %d, %Y")
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})




def book_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel, status='available')

    context = {
        'hotel': hotel,
        'rooms': rooms,
    }
    return render(request, 'bookings/booking.html', context)



def book_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel, status='available')

    context = {
        'hotel': hotel,
        'rooms': rooms,
    }
    return render(request, 'bookings/booking.html', context)


def add_review(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not rating or not comment:
            return JsonResponse({'success': False, 'error': 'Rating and comment are required.'})

        try:
            rating = int(rating)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid rating value.'})

        user = request.user if request.user.is_authenticated else User.objects.first()

        review = Review.objects.create(
            user=user,
            hotel=hotel,
            rating=rating,
            comment=comment,
            review_date=timezone.now()
        )

        avg_rating = Review.objects.filter(hotel=hotel).aggregate(Avg('rating'))['rating__avg'] or 0
        hotel.average_review = round(avg_rating, 1)
        hotel.save()

        return JsonResponse({
            'success': True,
            'username': user.username,
            'rating': rating,
            'comment': comment,
            'created_at': review.created_at.strftime("%b %d, %Y"),
        })

    return JsonResponse({'success': False, 'error': 'Invalid request.'})

def owner_register(request):
    return render(request, 'users/owner-register.html')

def properties(request):
    return render(request, 'hotels/new-hotel.html')



def all_hotels(request):
    return render(request, 'hotels/all-hotels.html')

def all_rooms(request):
    return render(request, 'hotels/all-rooms.html')



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
