from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'hotel', 'room', 'user', 'check_in', 'check_out', 'status', 'total_price', 'created_at'
    )
    list_filter = (
        'status', 'hotel', 'room', 'check_in', 'check_out', 'created_at'
    )
    search_fields = (
        'id', 'user__username', 'user__email', 'hotel__hotel_name', 'room__room_number', 'guest_first_name', 'guest_last_name', 'guest_email'
    )
    autocomplete_fields = ('user', 'hotel', 'room')
    date_hierarchy = 'check_in'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Booking', {
            'fields': ('hotel', 'room', 'user', 'status', 'check_in', 'check_out', 'num_guests', 'total_price')
        }),
        ('Guest snapshot', {
            'classes': ('collapse',),
            'fields': ('guest_first_name', 'guest_last_name', 'guest_email', 'guest_phone', 'guest_nationality', 'guest_dob', 'special_requests')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
