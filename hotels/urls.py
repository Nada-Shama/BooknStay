from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('all/', views.all_hotels, name='all_hotels'),
    path('rooms/', views.all_rooms, name='all_rooms'),
    path('<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('<int:hotel_id>/book/', views.book_room, name='book_room'),
    path('<int:hotel_id>/add_review/', views.add_review, name='add_review'),
    path('add/', views.properties, name='properties'), 

    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/new/', views.owner_add_room, name='owner_add_room'), 
    path('owner/hotel/new/', views.new_hotel, name='owner_hotel_new'),
]

