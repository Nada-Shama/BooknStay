import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from hotels.models import Hotel, Room


class Command(BaseCommand):
    help = "Seed the database with demo Hotels and Rooms (10 hotels, 4 rooms each). Safe to run multiple times."

    def add_arguments(self, parser):
        parser.add_argument('--hotels', type=int, default=10, help='Number of hotels to create (default: 10)')
        parser.add_argument('--rooms-per-hotel', type=int, default=4, help='Rooms per hotel (default: 4)')

    def handle(self, *args, **options):
        num_hotels = options['hotels']
        rooms_per_hotel = options['rooms_per_hotel']

        User = get_user_model()
        owner_email = 'owner@example.com'
        owner, _ = User.objects.get_or_create(
            email=owner_email,
            defaults={
                'username': 'owner_demo',
                'first_name': 'Demo',
                'last_name': 'Owner',
            }
        )
        if not owner.has_usable_password():
            owner.set_password('changeme123')
            owner.save()
        if hasattr(owner, 'role') and owner.role != 'owner':
            owner.role = 'owner'
            owner.save(update_fields=['role'])

        city_state = [
            ('Miami', 'FL', 'USA'), ('New York', 'NY', 'USA'), ('Los Angeles', 'CA', 'USA'),
            ('Chicago', 'IL', 'USA'), ('Austin', 'TX', 'USA'), ('Seattle', 'WA', 'USA'),
            ('Boston', 'MA', 'USA'), ('Denver', 'CO', 'USA'), ('Orlando', 'FL', 'USA'),
            ('San Diego', 'CA', 'USA'),
        ]

        property_types = ['Hotel', 'Resort', 'Boutique Hotel', 'Guest House', 'Apartment']
        amenities_pool = ['Free Wi‑Fi', 'Parking', 'Pool', 'Spa', 'Gym', 'Restaurant', 'Pet Friendly', 'Airport Shuttle']

        room_types = [
            (Room.SINGLE, 'Single', 1),
            (Room.DOUBLE, 'Double', 2),
            (Room.SUITE, 'Suite', 3),
        ]

        created_hotels = 0
        created_rooms = 0

        for i in range(num_hotels):
            city, state, country = city_state[i % len(city_state)]
            hotel_name = f"{random.choice(['Grand', 'Ocean', 'City', 'Sunset', 'Skyline', 'Lakeside', 'Royal', 'Harbor'])} {random.choice(['Hotel', 'Resort', 'Suites', 'Inn'])} {i+1}"
            hotel, created = Hotel.objects.get_or_create(
                hotel_name=hotel_name,
                defaults={
                    'owner': owner,
                    'property_type': random.choice(property_types),
                    'star_rating': random.randint(3, 5),
                    'address': f"{random.randint(100, 9999)} Main St",
                    'zipcode': str(random.randint(10000, 99999)),
                    'city': city,
                    'state': state,
                    'country': country,
                    'num_rooms': rooms_per_hotel,
                    'opening_date': date.today() - timedelta(days=random.randint(30, 3650)),
                    'amenities': random.sample(amenities_pool, k=random.randint(3, 6)),
                    'description': f"Welcome to {hotel_name}, a {random.choice(['vibrant', 'cozy', 'modern', 'luxury'])} property in {city}.",
                    'business_name': f"{hotel_name} LLC",
                    'tax_id': f"{random.randint(10,99)}-{random.randint(1000000,9999999)}",
                    'website': f"https://example.com/{hotel_name.replace(' ', '').lower()}",
                    'contact_preference': random.choice(['Email', 'Phone']),
                }
            )
            if created:
                created_hotels += 1

            # Rooms
            for r in range(rooms_per_hotel):
                rtype, _, capacity = random.choice(room_types)
                room_number = f"{random.randint(1, 15)}{random.choice(['01','02','03','04','05','06','07','08','09','10'])}"
                price = random.choice([89, 119, 149, 179, 199, 229, 249, 299])
                room, r_created = Room.objects.get_or_create(
                    hotel=hotel,
                    room_number=room_number,
                    defaults={
                        'type': rtype,
                        'capacity': capacity,
                        'price': price,
                        'beds': str(capacity),
                        'size': random.choice([18, 22, 28, 32, 40]),
                        'view': random.choice(['City', 'Garden', 'Sea', 'Standard']),
                        'floor': random.randint(1, 15),
                        'smoking': False,
                        'status': Room.AVAILABLE,
                        'description': f"Comfortable {rtype} room with essential amenities.",
                        'available_rooms': random.randint(1, 5),
                        'refundable': True,
                        'discount': 0,
                        'cancellation_policy': 'Free cancellation up to 24 hours before check-in.',
                    }
                )
                if r_created:
                    created_rooms += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: Hotels created={created_hotels}, Rooms created={created_rooms} (total hotels now {Hotel.objects.count()}, rooms {Room.objects.count()})"
        ))

