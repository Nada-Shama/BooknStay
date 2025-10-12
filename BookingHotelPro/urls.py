from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from hotels import views as hotel_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', hotel_views.home, name='home'),
    path('users/', include('users.urls')),
    path('hotels/', include('hotels.urls')),
    path('bookings/', include('bookings.urls')),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
