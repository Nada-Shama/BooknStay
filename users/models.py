from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('owner', 'Owner'),
        ('admin', 'Admin')
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=False)
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)

    def is_customer(self):
        return self.role == 'customer'

    def is_owner(self):
        return self.role == 'owner'

    def is_admin(self):
        return self.role == 'admin'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class FavoriteRoom(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='favorite_rooms')
    room = models.ForeignKey('hotels.Room', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'room')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ❤ Room {self.room_id}"
