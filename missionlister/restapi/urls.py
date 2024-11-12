from django.urls import path
from .views import get_missions, create_mission, mission_detail

urlpatterns = [
    path("missions/", get_missions, name="get_missions"),
    path("missions/create/", create_mission, name="create_mission"),
    path("missions/<int:pk>", mission_detail, name="mission_detail"),
]
