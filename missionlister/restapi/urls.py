from django.urls import path
from .views import get_missions, create_mission

urlpatterns = [
    path('missions/', get_missions, name='get_missions'),
    path('missions/create/', create_mission, name='create_mission')
]