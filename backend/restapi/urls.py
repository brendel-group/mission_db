from django.urls import include, path
from .views import (
    denied_topics,
    denied_topics_create,
    denied_topics_delete,
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
    set_was_modified,
    get_file_by_path,
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
        "topics/<path:file_path>",
        get_topics_from_files,
        name="get_topics_from_files",
    ),
    path(
        "topics-names",
        denied_topics,
        name="Denied_topics",
    ),
    path(
        "topics-names/create/",
        denied_topics_create,
        name="Denied_topics_create",
    ),
    path(
        "topics-names/<str:name>",
        denied_topics_delete,
        name="Denied_topics_delete",
    ),
    path(
        "missions/<int:pk>/was_modified",
        set_was_modified,
        name="set_was_modified",
    ),
    path("file/<path:file_path>", get_file_by_path, name="get_file_by_path"),
]
