from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('rooms/', views.all_rooms, name='all_rooms'),
    path('<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('<int:hotel_id>/book/', views.book_room, name='book_room'),
    
    path('<int:hotel_id>/add_review/', views.add_review, name='add_review'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),

    path('add/', views.properties, name='properties'), 
    path('all/', views.all_hotels, name='all_hotels'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/new/', views.owner_add_room, name='owner_add_room'), 
    path('owner/hotel/new/', views.new_hotel, name='owner_hotel_new'),
    
    path('owner/hotels/', views.owner_hotels, name='owner_hotels'),
    path('owner/hotel/<int:hotel_id>/', views.owner_hotel_detail, name='owner_hotel_detail'),
     path('owner/room/<int:room_id>/', views.owner_room_detail, name='owner_room_detail'),
     
     path('owner/hotel/<int:hotel_id>/photo_upload/', views.owner_hotel_photo_upload, name='owner_hotel_photo_upload'),
     path("delete_room_image/<int:image_id>/", views.delete_room_image, name="delete_room_image"),
     path('delete_hotel/<int:hotel_id>/', views.delete_hotel, name='delete_hotel'),
     path('owner/room/<int:room_id>/delete/', views.owner_room_delete, name='owner_room_delete'),
     
     path('search/', views.search_results, name='search_results'),
    
]
     


    

