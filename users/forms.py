from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.validators import RegexValidator
from django.utils.text import slugify
import uuid
from django.core.exceptions import ValidationError


phone_validator = RegexValidator(r'^\+?[0-9 ()-]{7,20}$', 'Enter a valid phone number.')

class CustomUserCreationForm(UserCreationForm):
    
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    phone = forms.CharField(required=True, validators=[phone_validator])
    date_of_birth = forms.DateField(required=False, input_formats=['%m/%d/%Y', '%Y-%m-%d'])
    nationality = forms.CharField(required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email    
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob.year < 1900:
            raise forms.ValidationError('Date of birth looks invalid.')
        return dob
    
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'nationality',
            'password1', 'password2'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        if not user.username: # that will get username from email ...
            email = self.cleaned_data.get('email') or ''
            base = slugify(email.split('@')[0]) or 'user'
            user.username = f"{base}-{uuid.uuid4().hex[:6]}"            
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email')
        user.phone = self.cleaned_data.get('phone')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.nationality = self.cleaned_data.get('nationality', '')
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(required=False, validators=[phone_validator])

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'nationality']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('This email is already in use.')
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()
