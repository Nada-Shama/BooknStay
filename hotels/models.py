from django.db import models
from users.models import User
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class Hotel(models.Model):
    HOTEL_TYPES = [
        ('Hotel', 'Hotel'),
        ('Resort', 'Resort'),
        ('Boutique Hotel', 'Boutique Hotel'),
        ('Guest House', 'Guest House'),
        ('Apartment', 'Apartment'),
    ]

    STAR_RATINGS = [(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, default=1)
    hotel_name = models.CharField(max_length=200 , default='Unnamed Hotel') 
    property_type = models.CharField(max_length=50, choices=HOTEL_TYPES, blank=True, null=True)
    star_rating = models.IntegerField(choices=STAR_RATINGS, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    num_rooms = models.IntegerField(blank=True, null=True)
    opening_date = models.DateField(blank=True, null=True)
    amenities = models.JSONField(default=list, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    business_name = models.CharField(max_length=200, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_preference = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='hotel_photos/', blank=True, null=True)

    def __str__(self):
        return self.hotel_name

class Room(models.Model):
    SINGLE = 'single'
    DOUBLE = 'double'
    SUITE = 'suite'
    ROOM_TYPE_CHOICES = [
        (SINGLE, 'Single'),
        (DOUBLE, 'Double'),
        (SUITE, 'Suite'),
    ]

    AVAILABLE = 'available'
    BOOKED = 'booked'
    STATUS_CHOICES = [
        (AVAILABLE, 'Available'),
        (BOOKED, 'Booked'),
    ]

    hotel = models.ForeignKey(
        'Hotel',
        on_delete=models.CASCADE,
        related_name='rooms'
    )


    room_number = models.CharField(max_length=50)   
    price = models.DecimalField(max_digits=10, decimal_places=2)  

    type = models.CharField(
        max_length=50,
        choices=ROOM_TYPE_CHOICES,
        default=SINGLE,
        blank=True,
        null=True
    )
    capacity = models.IntegerField(default=1, blank=True, null=True)
    beds = models.CharField(max_length=50, default='1', blank=True, null=True)
    size = models.IntegerField(default=20, blank=True, null=True)
    view = models.CharField(max_length=50, default='Standard', blank=True, null=True)
    floor = models.IntegerField(default=1, blank=True, null=True)
    smoking = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=AVAILABLE,
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    available_rooms = models.IntegerField(default=1, blank=True, null=True)
    refundable = models.BooleanField(default=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True, null=True)
    cancellation_policy = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hotel.hotel_name} - Room {self.room_number} ({self.type or 'N/A'})"


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rooms/')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Image for {self.room.hotel.hotel_name} - Room {self.room.room_number}"
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField() 
    comment = models.TextField()
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
