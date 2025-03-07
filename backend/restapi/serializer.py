from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.db.models import Sum
from .models import Denied_topics, Mission, Topic
from .models import File
from .models import Tag
from .models import Mission_tags


class MissionSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField()
    total_size = serializers.SerializerMethodField()
    robots = serializers.SerializerMethodField()

    class Meta:  # definition of which data to serialize
        model = Mission
        fields = "__all__"

    def get_total_duration(self, obj):
        # calculate the total duration of all files in the mission
        result = File.objects.filter(mission=obj).aggregate(Sum("duration"))
        return result["duration__sum"] or 0

    def get_total_size(self, obj):
        # calculate the total size of all files in the mission
        result = File.objects.filter(mission=obj).aggregate(Sum("size"))
        return result["size__sum"] or 0

    def get_robots(self, obj):
        # get all robot names in the mission
        result = list(
            File.objects.filter(mission=obj).values_list("robot", flat=True).distinct()
        )
        if None in result:
            result.remove(None)
        result = ", ".join(result)
        return result


class MissionWasModifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ["id", "was_modified"]


class FileSerializer(serializers.ModelSerializer):
    file_path = serializers.CharField(source="file.name", initial=None)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            "id",
            "file_path",
            "file_url",
            "robot",
            "duration",
            "size",
            "type",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        url = obj.file.url
        if request and hasattr(request, "session"):
            sessionid = request.session.session_key
            url += f"?sessionid={sessionid}"
        return url


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
    video_path = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            "name",
            "type",
            "message_count",
            "frequency",
            "video_path",
            "video_url",
        ]

    def get_video_url(self, obj):
        if not obj.video:
            return None

        request = self.context.get("request")
        url = obj.video.url.replace("/download/", "/stream/")
        if request and hasattr(request, "session"):
            sessionid = request.session.session_key
            url += f"?sessionid={sessionid}"
        return url

    def get_video_path(self, obj):
        if obj.video:
            return obj.video.name
        return None


class DeniedTopicNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Denied_topics
        fields = ["name"]
