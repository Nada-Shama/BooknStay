from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room, Review
from django.db.models import Avg
from django.contrib import messages
from users.models import User


def home(request):
    hotels = Hotel.objects.all()
    return render(request, 'users/home.html', {'hotels': hotels})


def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotels/hotels.html', {'hotels': hotels})


def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel)
    reviews = Review.objects.filter(hotel=hotel)

    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        hotel.average_review = round(avg_rating, 1)
        hotel.save()

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'reviews': reviews,
    }
    return render(request, 'hotels/property-details.html', context)


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
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment')

        user = request.user if request.user.is_authenticated else User.objects.first()

        Review.objects.create(
            user=user,
            hotel=hotel,
            rating=rating,
            comment=comment,
            review_date=None
        )

        avg_rating = Review.objects.filter(hotel=hotel).aggregate(Avg('rating'))['rating__avg']
        hotel.average_review = round(avg_rating, 1)
        hotel.save()

        messages.success(request, "Your review has been added!")
        return redirect('hotels:hotel_detail', hotel_id=hotel.id)

    return render(request, 'hotels/add_review.html', {'hotel': hotel})


def owner_register(request):
    return render(request, 'users/owner-register.html')

def properties(request):

    
    return render(request, 'hotels/properties.html')