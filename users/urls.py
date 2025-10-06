from django.urls import path
from . import views
from hotels import views as hotel_views

urlpatterns = [
    path('auth/', views.login_register, name='login_register'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('property-details/<int:hotel_id>/', hotel_views.hotel_detail, name='property-details'),
    path('owner/register/', views.owner_register, name='owner-register'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('account/', views.account, name='account'),


    #path('search-hotels/', views.hotels_search_results, name='hotels_search_results'),
    #path('hotels/all/', views.all_hotels, name='all_hotels'),

    #path('booking/', views.booking, name='booking'),

    #path('owner/hotels/rooms/new/', views.owner_add_room, name='owner_add_room'),
    #path('rooms/<int:room_id>/', views.room_details, name='room_details'),
]
