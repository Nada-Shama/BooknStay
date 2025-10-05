from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/', views.booking, name='booking'),
    path('contact/',views.contact, name='contact')
]
