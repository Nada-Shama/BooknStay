from django.shortcuts import render
from django.shortcuts import get_object_or_404
from hotels.models import Hotel, Room

# Create your views here.
def booking(request, hotel_id):
    """Handle hotel booking page for both guests and authenticated users"""
    rooms = Room.objects.filter(hotel__id=hotel_id, status='available')
    context = {
        'hotel': get_object_or_404(Hotel, id=hotel_id),
        'rooms': rooms,
        #'user': request.user,
    }
    return render(request, 'bookings/booking.html', context)
