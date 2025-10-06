from django.urls import path
from . import views
from hotels import views as hotel_views

urlpatterns = [
    path('<int:hotel_id>/', views.booking, name='booking'),
    path('hotels/<int:hotel_id>/', hotel_views.hotel_detail, name='hotels'),
]
