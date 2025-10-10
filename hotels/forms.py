from django import forms
from .models import Room, Hotel



class HotelForm(forms.ModelForm):
    agree_terms = forms.BooleanField(
        required=True,
        label="I agree to the terms and conditions"
    )

    amenities = forms.MultipleChoiceField(
        choices=[
            ('Free Wi‑Fi', 'Free Wi‑Fi'),
            ('Parking', 'Parking'),
            ('Pool', 'Pool'),
            ('Spa', 'Spa'),
            ('Gym', 'Gym'),
            ('Restaurant', 'Restaurant'),
            ('Pet Friendly', 'Pet Friendly'),
            ('Airport Shuttle', 'Airport Shuttle'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Hotel
        fields = [
            'hotel_name',
            'property_type',
            'star_rating',
            'address',
            'zipcode',
            'city',
            'state',
            'country',
            'num_rooms',
            'opening_date',
            'amenities',
            'description',
            'business_name',
            'tax_id',
            'website',
            'contact_preference',
            'photo',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'placeholder': 'Tell us about your property...'}),
            'opening_date': forms.DateInput(attrs={'type': 'date'}),
        }

class RoomForm(forms.ModelForm):
    images = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(),
        help_text="Upload one or more images (JPG/PNG)."
    )

    class Meta:
        model = Room
        fields = [
            'room_number', 'type', 'capacity', 'price', 'beds', 'size',
            'view', 'floor', 'smoking', 'status', 'description',
            'available_rooms', 'refundable', 'discount', 'cancellation_policy'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'cancellation_policy': forms.Textarea(attrs={'rows': 3}),
        }
        
        
        
        
from .models import RoomImage

class RoomImageForm(forms.ModelForm):
    class Meta:
        model = RoomImage
        fields = ['image']