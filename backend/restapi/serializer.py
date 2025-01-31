from rest_framework import serializers
from rest_framework.exceptions import NotFound
from .models import Allowed_topic_names, Mission, Topic
from .models import File
from .models import Tag
from .models import Mission_tags


class MissionSerializer(serializers.ModelSerializer):
    class Meta:  # definition of which data to serialize
        model = Mission
        fields = "__all__"


class MissionWasModifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ["id", "was_modified"]


class FileSerializer(serializers.ModelSerializer):
    file_path = serializers.CharField(source="file.path", initial=None)
    file_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id",
            "file_path",
            "file_url",
            "video",
            "video_url",
            "robot",
            "duration",
            "size",
            "type",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "session"):
            sessionid = request.session.session_key
        if sessionid:
            url = f"{obj.file.url}?sessionid={sessionid}"
            return url
        return None

    def get_video_url(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "session"):
            sessionid = request.session.session_key
        if sessionid and obj.video:
            url = f"{obj.video.url.replace('/download/', '/stream/')}?sessionid={sessionid}"
            return url
        return None


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class MissionTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source="tag.name", initial=None)

    mission_id = serializers.IntegerField(source="mission.id", initial=None)

    class Meta:
        model = Mission_tags
        fields = ["mission_id", "tag_name"]
        extra_kwargs = {
            "mission_id": {"write_only": True},  # Used only for input
            "tag_name": {"write_only": True},  # Used only for input
        }

    def create(self, validated_data):
        """
        Create tag mission-tag using mission id and tag name
        Creates new tag when tag doesn't exist
        ### Parameters
        validated_data: data that contains the mission id and tag name
        ### Raises
        NotFound: if mission with mission id is not found
        """
        mission_id = validated_data.pop("mission").get("id")
        tag_name = validated_data.pop("tag").get("name")
        try:
            mission = Mission.objects.get(id=mission_id)
        except Mission.DoesNotExist:
            raise NotFound(f"Mission with id {mission_id} not found")
        tag, self.tag_created = Tag.objects.get_or_create(name=tag_name)
        mission_tag, _ = Mission_tags.objects.get_or_create(mission=mission, tag=tag)
        return mission_tag


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ["id", "name", "type", "message_count", "frequency"]


class AllowedTopicNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allowed_topic_names
        fields = ["name"]
