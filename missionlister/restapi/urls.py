from django.urls import path
from .views import get_mission

urlpatterns = [
    path('missions/', get_mission, name='get_mission')
]