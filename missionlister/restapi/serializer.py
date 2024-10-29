from rest_framework import serializers
from .models import Mission

class MissionSerializer(serializers.ModelSerializer):
    class Meta: # definition of which data to serialize
        model = Mission 
        fields = '__all__'


