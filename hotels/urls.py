from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.hotel_list, name='hotel_list'),
    path('<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('<int:hotel_id>/book/', views.book_room, name='book_room'),
    path('<int:hotel_id>/add_review/', views.add_review, name='add_review'),
    path('add/', views.properties, name='properties'), 

]

