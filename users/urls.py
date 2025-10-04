from django.urls import path
from . import views

urlpatterns = [
    #path('register/', views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    path('auth/', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('properties/', views.properties, name='properties'),
    path('property-details/', views.property_details, name='property-details'),
    path('contact/', views.contact, name='contact'),
]
