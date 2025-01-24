from django.urls import include, path
from .views import (
    get_missions,
    create_mission,
    get_topics_from_files,
    mission_detail,
    get_tags,
    create_tag,
    tag_detail,
    MissionByTagAPI,
    TagByMissionAPI,
    add_tag_to_mission,
    delete_mission_tag,
    get_files_by_mission_id,
)

urlpatterns = [
    path("missions/", get_missions, name="get_missions"),
    path("missions/create/", create_mission, name="create_mission"),
    path("missions/<int:pk>", mission_detail, name="mission_detail"),
    path(
        "missions/tags/<int:id>",
        TagByMissionAPI.as_view(),
        name="get_tags_by_mission_id",
    ),
    path("tags/", get_tags, name="get_tags"),
    path("tags/create/", create_tag, name="create_tag"),
    path("tags/<str:name>", tag_detail, name="tag_detail"),
    path(
        "tags/missions/<str:name>",
        MissionByTagAPI.as_view(),
        name="get_missions_by_tag",
    ),
    path("mission-tags/create/", add_tag_to_mission, name="add_tag_to_mission"),
    path(
        "mission-tags/delete/<int:mission_id>/<str:tag_name>",
        delete_mission_tag,
        name="delete_mission_tag",
    ),
    path(
        "missions/<int:mission_id>/files/",
        get_files_by_mission_id,
        name="get_files_by_mission_id",
    ),
    path("auth/", include("dj_rest_auth.urls")),
    path(
        "missions/<str:file_path>/files/topics",
        get_topics_from_files,
        name="get_topics_from_files",
    ),
]
