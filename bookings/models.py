from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    hotel = models.ForeignKey('hotels.Hotel', on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE, related_name='bookings')

    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.IntegerField(default=1)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Booking #{self.id or 'new'} • {self.room_id} • {self.check_in}→{self.check_out}"

    def clean(self):
        # Basic date validation
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValueError('Check-out must be after check-in')

    @staticmethod
    def is_room_available(room, check_in: date, check_out: date) -> bool:
        """
        A room is available if overlapping (non-cancelled) bookings are less than the room's available_rooms
        Overlap condition: existing.check_in < check_out and existing.check_out > check_in
        """
        if room.status == 'booked':
            return False

        overlapping = Booking.objects.filter(
            room=room,
            status__in=[Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED],
            check_in__lt=check_out,
            check_out__gt=check_in,
        ).count()

        capacity = room.available_rooms or 1
        return overlapping < capacity

    def compute_total_price(self) -> None:
        nights = (self.check_out - self.check_in).days
        nights = max(nights, 1)
        self.total_price = (self.room.price or 0) * nights
