from django.urls import path
from . import views
from hotels import views as hotel_views

urlpatterns = [
    path('auth/', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/',views.contact, name='contact'),
    path('property-details/', hotel_views.hotel_detail, name='property-details'),
    path('owner/register/', views.owner_register, name='owner-register'),
]
