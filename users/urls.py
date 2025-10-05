from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('hotels/', views.hotels, name='hotels'),
    path('booking/', views.booking, name='booking'),
    path('owner/register/', views.owner_register, name='owner-register'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('account/', views.account, name='account'),
    path('properties/', views.properties, name='properties'),
    path('property-details/', views.property_details, name='property-details'),
    path('contact/', views.contact, name='contact'),
]
