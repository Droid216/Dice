from django.contrib import admin
from django.urls import path
from dice_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.RecordsView.as_view(), name='records'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('about_us/', views.RecordsView.as_view(), name='records'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
