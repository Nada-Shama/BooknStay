import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from bookings.models import Booking
from hotels.models import Room, Hotel


class Command(BaseCommand):
    help = "Create random reservations for a given user email. Example: python manage.py seed_user_reservations --email jouly@zughbor.com --count 10"

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Email of the user to create bookings for')
        parser.add_argument('--count', type=int, default=10, help='Number of reservations to create (default: 10)')
        parser.add_argument('--window-days', type=int, default=90, help='Create bookings within N days from today (default: 90)')
        parser.add_argument('--max-nights', type=int, default=5, help='Maximum nights per reservation (default: 5)')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        count = options['count']
        window_days = max(7, options['window_days'])
        max_nights = max(1, options['max_nights'])

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0][:20] or 'user',
                'first_name': email.split('@')[0].title(),
            }
        )
        if created:
            # Set a temporary password so account is usable if needed
            user.set_password(User.objects.make_random_password())
            user.save()

        rooms = list(Room.objects.select_related('hotel').all())
        if not rooms:
            raise CommandError('No rooms available. Seed hotels/rooms first (e.g., seed_demo_data).')

        created_bookings = 0
        attempts = 0
        max_attempts = count * 20  # generous to find availability without infinite loops

        today = date.today()

        while created_bookings < count and attempts < max_attempts:
            attempts += 1
            room = random.choice(rooms)
            # Choose a check-in 1..window_days days from today, random length 1..max_nights
            start_offset = random.randint(1, window_days)
            nights = random.randint(1, max_nights)
            check_in = today + timedelta(days=start_offset)
            check_out = check_in + timedelta(days=nights)

            if not Booking.is_room_available(room, check_in, check_out):
                continue

            booking = Booking(
                user=user,
                hotel=room.hotel,
                room=room,
                check_in=check_in,
                check_out=check_out,
                num_guests=min(room.capacity or 1, 2),
                status=Booking.STATUS_CONFIRMED,
                guest_first_name=getattr(user, 'first_name', '') or 'Guest',
                guest_last_name=getattr(user, 'last_name', '') or '',
                guest_email=user.email,
                guest_phone=getattr(user, 'phone', ''),
                guest_nationality=getattr(user, 'nationality', ''),
            )
            booking.compute_total_price()
            try:
                booking.save()
                created_bookings += 1
            except Exception as e:
                # Skip and try another
                continue

        if created_bookings < count:
            self.stdout.write(self.style.WARNING(
                f"Created {created_bookings}/{count} reservations; ran out of available slots or attempts."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully created {created_bookings} reservations for {email}."
            ))

