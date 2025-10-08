from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import datetime
from hotels.models import Hotel, Room
from .models import Booking

# Create your views here.
def booking(request, hotel_id):
    """Render hotel booking page with available rooms"""
    rooms = Room.objects.filter(hotel__id=hotel_id, status='available')
    context = {
        'hotel': get_object_or_404(Hotel, id=hotel_id),
        'rooms': rooms,
    }
    return render(request, 'bookings/booking.html', context)


@login_required
@require_http_methods(["POST"])
def create_booking(request, hotel_id):
    """Create a booking with availability check; returns JSON."""
    try:
        hotel = get_object_or_404(Hotel, id=hotel_id)
        room_id = request.POST.get('room_id')
        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        num_guests = int(request.POST.get('num_guests') or 1)
        # Guest details (optional)
        guest_first_name = (request.POST.get('firstName') or '').strip()
        guest_last_name = (request.POST.get('lastName') or '').strip()
        guest_email = (request.POST.get('email') or '').strip()
        guest_phone = (request.POST.get('phone') or '').strip()
        guest_nationality = (request.POST.get('nationality') or '').strip()
        guest_dob = (request.POST.get('dob') or '').strip()
        special_requests = (request.POST.get('specialRequests') or '').strip()

        if not room_id or not check_in_str or not check_out_str:
            return JsonResponse({'success': False, 'error': 'room_id, check_in, check_out are required.'}, status=400)

        room = get_object_or_404(Room, id=room_id, hotel=hotel)

        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()

        if check_in >= check_out:
            return JsonResponse({'success': False, 'error': 'check_out must be after check_in.'}, status=400)

        if not Booking.is_room_available(room, check_in, check_out):
            return JsonResponse({'success': False, 'error': 'Room not available for the selected dates.'}, status=409)

        booking = Booking(
            user=request.user,
            hotel=hotel,
            room=room,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            status=Booking.STATUS_CONFIRMED,
            guest_first_name=guest_first_name or getattr(request.user, 'first_name', ''),
            guest_last_name=guest_last_name or getattr(request.user, 'last_name', ''),
            guest_email=guest_email or getattr(request.user, 'email', ''),
            guest_phone=guest_phone or getattr(request.user, 'phone', ''),
            guest_nationality=guest_nationality or getattr(request.user, 'nationality', ''),
            guest_dob=guest_dob or getattr(request.user, 'date_of_birth', None),
            special_requests=special_requests,
        )
        booking.compute_total_price()
        booking.save()

        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'hotel_id': hotel.id,
            'room_id': room.id,
            'check_in': str(booking.check_in),
            'check_out': str(booking.check_out),
            'total_price': float(booking.total_price),
            'status': booking.status,
        }, status=201)

    except ValueError as ve:
        return JsonResponse({'success': False, 'error': str(ve)}, status=400)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Unexpected error while creating booking.'}, status=500)


def _can_manage_booking(user, booking: Booking) -> bool:
    if not user.is_authenticated:
        return False
    if booking.user_id and booking.user_id == user.id:
        return True
    # owner or staff/superuser can manage bookings of their hotels
    is_owner = getattr(user, 'is_owner', lambda: False)()
    if is_owner and booking.hotel.owner_id == user.id:
        return True
    return user.is_staff or getattr(user, 'is_admin', lambda: False)() or user.is_superuser


@login_required
@require_http_methods(["POST"])
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not _can_manage_booking(request.user, booking):
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)

    if booking.status == Booking.STATUS_CANCELLED:
        return JsonResponse({'success': True, 'status': booking.status})

    booking.status = Booking.STATUS_CANCELLED
    booking.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'success': True, 'status': booking.status})


@login_required
@require_http_methods(["POST"])
def modify_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not _can_manage_booking(request.user, booking):
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)

    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')
    num_guests_str = request.POST.get('num_guests')

    if not check_in_str or not check_out_str:
        return JsonResponse({'success': False, 'error': 'check_in and check_out are required.'}, status=400)

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        if num_guests_str:
            booking.num_guests = int(num_guests_str)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid date or guests.'}, status=400)

    if check_in >= check_out:
        return JsonResponse({'success': False, 'error': 'check_out must be after check_in.'}, status=400)

    # Check availability excluding this booking
    from django.db.models import Q
    overlapping = Booking.objects.filter(
        room=booking.room,
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exclude(id=booking.id).count()
    capacity = booking.room.available_rooms or 1
    if overlapping >= capacity:
        return JsonResponse({'success': False, 'error': 'Room not available for the selected dates.'}, status=409)

    booking.check_in = check_in
    booking.check_out = check_out
    booking.compute_total_price()
    booking.save()

    return JsonResponse({
        'success': True,
        'booking_id': booking.id,
        'check_in': str(booking.check_in),
        'check_out': str(booking.check_out),
        'num_guests': booking.num_guests,
        'total_price': float(booking.total_price),
        'status': booking.status,
    })
