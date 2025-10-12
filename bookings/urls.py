from django.urls import path
from . import views
from hotels import views as hotel_views

urlpatterns = [
    path('<int:hotel_id>/', views.booking, name='booking'),
    path('<int:hotel_id>/create/', views.create_booking, name='create_booking'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('modify/<int:booking_id>/', views.modify_booking, name='modify_booking'),
    path('hotels/<int:hotel_id>/', hotel_views.hotel_detail, name='hotels'),
    # Owner management APIs (AJAX)
    path('owner/calendar/', views.owner_bookings_calendar_data, name='owner_bookings_calendar_data'),
    path('owner/list/', views.owner_bookings_list, name='owner_bookings_list'),
    path('owner/detail/<int:booking_id>/', views.owner_booking_detail, name='owner_booking_detail'),
    path('owner/update/<int:booking_id>/', views.owner_update_booking, name='owner_update_booking'),
    path('owner/delete/<int:booking_id>/', views.owner_delete_booking, name='owner_delete_booking'),
    path('owner/approve/<int:booking_id>/', views.owner_approve_booking, name='owner_approve_booking'),
    path('owner/deny/<int:booking_id>/', views.owner_deny_booking, name='owner_deny_booking'),
]
