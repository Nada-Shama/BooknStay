from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, login
from datetime import datetime, date
from hotels.models import Hotel, Room
from .models import Booking
from calendar import monthrange

# Create your views here.
def booking(request, hotel_id):
    """Render hotel booking page with available rooms"""
    rooms = Room.objects.filter(hotel__id=hotel_id, status='available')
    context = {
        'hotel': get_object_or_404(Hotel, id=hotel_id),
        'rooms': rooms,
    }
    return render(request, 'bookings/booking.html', context)


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

        # If guest booking, optionally create a user account and log them in
        user_for_booking = request.user if request.user.is_authenticated else None
        if user_for_booking is None and guest_email:
            UserModel = get_user_model()
            existing = UserModel.objects.filter(email=guest_email).first()
            if existing:
                user_for_booking = existing
            else:
                base_username = (guest_email.split('@')[0] if guest_email else 'guest')[:20] or 'guest'
                candidate = base_username
                idx = 1
                while UserModel.objects.filter(username=candidate).exists():
                    candidate = f"{base_username}{idx}"
                    idx += 1
                temp_password = UserModel.objects.make_random_password()
                user_for_booking = UserModel.objects.create_user(
                    username=candidate,
                    email=guest_email,
                    password=temp_password,
                    first_name=guest_first_name,
                    last_name=guest_last_name,
                )
                try:
                    # Save optional extras if the custom user has these fields
                    if hasattr(user_for_booking, 'phone'):
                        user_for_booking.phone = guest_phone
                    if hasattr(user_for_booking, 'nationality'):
                        user_for_booking.nationality = guest_nationality
                    if hasattr(user_for_booking, 'date_of_birth') and guest_dob:
                        user_for_booking.date_of_birth = datetime.strptime(guest_dob, '%Y-%m-%d').date()
                    user_for_booking.save()
                except Exception:
                    pass

                # Log the new user in and set a session flag to prompt password setup
                login(request, user_for_booking)
                request.session['needs_password_setup'] = True

        booking = Booking(
            user=user_for_booking,
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
            guest_dob=(datetime.strptime(guest_dob, '%Y-%m-%d').date() if guest_dob else getattr(request.user, 'date_of_birth', None)),
            special_requests=special_requests,
        )
        booking.compute_total_price()
        booking.save()

        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'hotel_id': hotel.id,
            'hotel_name': hotel.hotel_name,
            'room_id': room.id,
            'room_number': room.room_number,
            'room_type': room.get_type_display() if hasattr(room, 'get_type_display') else (room.type or ''),
            'check_in': str(booking.check_in),
            'check_out': str(booking.check_out),
            'nights': (booking.check_out - booking.check_in).days,
            'num_guests': booking.num_guests,
            'total_price': float(booking.total_price),
            'status': booking.status,
            'guest_email': booking.guest_email or (request.user.email if request.user.is_authenticated else ''),
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
    # If previously cancelled, move to under_review upon edit request
    if booking.status == Booking.STATUS_CANCELLED:
        booking.status = Booking.STATUS_UNDER_REVIEW
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


@login_required
@require_http_methods(["GET"])
def owner_bookings_calendar_data(request):
    """Return per-day booking counts for a given room/month (owner/admin only)."""
    room_id = request.GET.get('room_id')
    if not room_id:
        return JsonResponse({'error': 'room_id is required'}, status=400)
    year = int(request.GET.get('year') or date.today().year)
    month = int(request.GET.get('month') or date.today().month)

    # Validate and authorize
    try:
        room = Room.objects.select_related('hotel').get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

    user = request.user
    is_owner = getattr(user, 'is_owner', lambda: False)()
    if not (user.is_staff or user.is_superuser or (is_owner and room.hotel.owner_id == user.id)):
        return JsonResponse({'error': 'Not authorized'}, status=403)

    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Overlapping bookings in month
    bookings = Booking.objects.filter(
        room=room,
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
        check_in__lte=last_day,
        check_out__gte=first_day,
    ).values('check_in', 'check_out')

    counts = {d: 0 for d in range(1, monthrange(year, month)[1] + 1)}
    for b in bookings:
        start = max(b['check_in'], first_day)
        end = min(b['check_out'], last_day)
        cur = start
        while cur <= end:
            # Count nights (exclude checkout day)
            if cur < b['check_out']:
                counts[cur.day] += 1
            # add one day safely
            cur = cur + (last_day - last_day.replace(day=last_day.day - 1))

    def color_for(count: int) -> str:
        if count >= 10:
            return '#e74c3c'
        if count >= 5:
            return '#f39c12'
        return '#2ecc71'

    events = []
    for d, c in counts.items():
        if c <= 0:
            continue
        events.append({
            'title': f'{c} bookings',
            'start': f'{year}-{month:02d}-{d:02d}',
            'color': color_for(c),
            'allDay': True,
        })
    return JsonResponse(events, safe=False)

@login_required
@require_http_methods(["GET"])
def owner_bookings_list(request):
    """Return bookings for a given room with basic details; filter by day/week/month optionally."""
    room_id = request.GET.get('room_id')
    if not room_id:
        return JsonResponse({'results': [], 'error': 'room_id is required'}, status=400)
    view = (request.GET.get('view') or 'month').lower()  # day|week|month
    y = int(request.GET.get('year') or date.today().year)
    m = int(request.GET.get('month') or date.today().month)
    d = int(request.GET.get('day') or 1)

    try:
        room = Room.objects.select_related('hotel').get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

    user = request.user
    is_owner = getattr(user, 'is_owner', lambda: False)()
    if not (user.is_staff or user.is_superuser or (is_owner and room.hotel.owner_id == user.id)):
        return JsonResponse({'error': 'Not authorized'}, status=403)

    start = date(y, m, d)
    if view == 'day':
        end = start
    elif view == 'week':
        # assume week starting on start date, 7 days window
        end = date(y, m, d) if d + 6 <= monthrange(y, m)[1] else date(y, m, monthrange(y, m)[1])
    else:
        # month
        start = date(y, m, 1)
        end = date(y, m, monthrange(y, m)[1])

    qs = Booking.objects.filter(
        room=room,
        check_in__lte=end,
        check_out__gte=start,
    ).select_related('user')

    def paid_status(b: Booking) -> str:
        # Placeholder: no payments model yet
        return 'Paid' if b.status == Booking.STATUS_CONFIRMED else 'Unpaid'

    data = []
    for b in qs:
        data.append({
            'id': b.id,
            'guest': (b.user.username if b.user else (b.guest_first_name or '-') ),
            'check_in': b.check_in.isoformat(),
            'check_out': b.check_out.isoformat(),
            'nights': (b.check_out - b.check_in).days,
            'price_per_night': float(b.room.price),
            'total_price': float(b.total_price),
            'paid': paid_status(b),
            'first_time_guest': 'Yes' if (b.user and b.user.bookings.exclude(id=b.id).count()==0) else 'No',
            'status': b.status,
        })

    return JsonResponse({'results': data})


@login_required
@require_http_methods(["POST"])
def owner_update_booking(request, booking_id):
    """Update booking dates/guests via owner management."""
    booking = get_object_or_404(Booking, id=booking_id)
    user = request.user
    is_owner = getattr(user, 'is_owner', lambda: False)()
    if not (user.is_staff or user.is_superuser or (is_owner and booking.hotel.owner_id == user.id)):
        return JsonResponse({'error': 'Not authorized'}, status=403)

    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')
    num_guests_str = request.POST.get('num_guests')

    if check_in_str:
        try:
            booking.check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid check_in'}, status=400)
    if check_out_str:
        try:
            booking.check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid check_out'}, status=400)
    if num_guests_str:
        try:
            booking.num_guests = int(num_guests_str)
        except ValueError:
            return JsonResponse({'error': 'Invalid guests'}, status=400)

    if booking.check_in >= booking.check_out:
        return JsonResponse({'error': 'check_out must be after check_in'}, status=400)

    # Availability check excluding current booking
    overlapping = Booking.objects.filter(
        room=booking.room,
        status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
        check_in__lt=booking.check_out,
        check_out__gt=booking.check_in,
    ).exclude(id=booking.id).count()
    capacity = booking.room.available_rooms or 1
    if overlapping >= capacity:
        return JsonResponse({'error': 'Room not available for the selected dates.'}, status=409)

    booking.compute_total_price()
    booking.save()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def owner_delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user = request.user
    is_owner = getattr(user, 'is_owner', lambda: False)()
    if not (user.is_staff or user.is_superuser or (is_owner and booking.hotel.owner_id == user.id)):
        return JsonResponse({'error': 'Not authorized'}, status=403)
    booking.delete()
    return JsonResponse({'success': True})
