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
    class Meta:
        model = Mission_tags
        fields = '__all__'
