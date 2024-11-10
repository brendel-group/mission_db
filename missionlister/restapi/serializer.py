from rest_framework import serializers
from .models import Mission
from .models import Tag
from .models import Mission_tags


class MissionSerializer(serializers.ModelSerializer):
    class Meta:  # definition of which data to serialize
        model = Mission
        fields = "__all__"

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class MissionTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(source='tag.name', initial=None)

    mission_id = serializers.IntegerField(source='mission.id', initial=None)

    class Meta:
        model = Mission_tags
        fields = ['mission_id','tag_name']
        extra_kwargs = {
            'mission_id': {'write_only': True},  # Used only for input
            'tag_name': {'write_only': True}  # Used only for input
        }

    def create(self,validated_data):
        mission_id = validated_data.pop('mission').get('id')
        tag_name = validated_data.pop('tag').get('name')
        mission = Mission.objects.get(id=mission_id)
        tag,_ = Tag.objects.get_or_create(name=tag_name)
        mission_tag,_ = Mission_tags.objects.get_or_create(
            mission=mission,
            tag=tag
        )
        return mission_tag

