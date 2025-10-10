from django.contrib import admin
from .models import Hotel, Room, RoomImage, Review


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    search_fields = ('hotel_name', 'city', 'country', 'owner__username')
    list_display = ('id', 'hotel_name', 'city', 'country', 'star_rating', 'owner', 'created_at')
    list_filter = ('city', 'country', 'star_rating', 'created_at')
    autocomplete_fields = ('owner',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    search_fields = ('room_number', 'hotel__hotel_name')
    list_display = ('id', 'hotel', 'room_number', 'type', 'price', 'status', 'available_rooms')
    list_filter = ('status', 'type', 'hotel')
    autocomplete_fields = ('hotel',)


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'created_at')
    autocomplete_fields = ('room',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel', 'user', 'rating', 'review_date')
    search_fields = ('hotel__hotel_name', 'user__username')
    list_filter = ('rating', 'review_date')
