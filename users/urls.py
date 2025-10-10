from django.urls import path
from . import views
from hotels import views as hotel_views
from . import views as user_views

urlpatterns = [
    path('auth/', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('property-details/<int:hotel_id>/', hotel_views.hotel_detail, name='property-details'),
    path('owner/register/', views.owner_register, name='owner-register'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/bookings-management/', views.owner_bookings_management, name='owner_bookings_management'),
    path('owner/profile/', views.owner_profile, name='owner_profile'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    
    path('owner/bookings-calendar-data/', views.owner_bookings_calendar_data, name='owner_bookings_calendar_data'),
    path('account/', views.account, name='account'),
    path('reservations/', views.reservations, name='reservations'),
    path('settings/', views.settings_view, name='settings'),

    # Favorites
    path('favorites/add/<int:room_id>/', user_views.add_favorite_room, name='add_favorite_room'),
    path('favorites/remove/<int:room_id>/', user_views.remove_favorite_room, name='remove_favorite_room'),
    path('favorites/', user_views.list_favorites, name='list_favorites'),

    # AJAX password validation
    path('ajax/validate-password/', user_views.validate_password_ajax, name='validate_password_ajax'),
    # Owner calendar data for management page
    path('owner/bookings-calendar-data/', views.owner_bookings_calendar_data, name='owner_bookings_calendar_data'),


    #path('search-hotels/', views.hotels_search_results, name='hotels_search_results'),
    #path('hotels/all/', views.all_hotels, name='all_hotels'),

    #path('booking/', views.booking, name='booking'),

]
