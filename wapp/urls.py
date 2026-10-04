from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('city-autocomplete/', views.city_autocomplete, name='city_autocomplete'),
    path('pin/', views.pin_location, name='pin_location'),
]