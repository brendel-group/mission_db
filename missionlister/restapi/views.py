from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *


@api_view(["GET"])
def get_missions(request):
    missions = Mission.objects.all()
    serializer = MissionSerializer(missions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_mission(request):
    serializer = MissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def mission_detail(request, pk):
    try:
        mission = Mission.objects.get(pk=pk)
    except mission.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = MissionSerializer(mission)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = MissionSerializer(mission, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        mission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_tags(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)

@api_view(["POST"])
def create_tag(request):
    serializer = TagSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def tag_detail(request, name):
    try:
        tag = Tag.objects.get(name=name)
    except tag.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MissionByTagAPI(generics.ListAPIView):
    serializer_class = MissionSerializer
    name="Get Missions by Tag"

    def get_queryset(self):
        try:
            tag = Tag.objects.get(name=self.kwargs['name'])
        except tag.DoesNotExist:
            return Mission.objects.none()

        mission_ids = Mission_tags.objects.filter(tag=tag).values_list('mission_id', flat=True)
        return  Mission.objects.filter(id__in=mission_ids)

class TagByMissionAPI(generics.ListAPIView):
    serializer_class = TagSerializer
    name="Get Tags by Mission id"

    def get_queryset(self):
        try:
            mission = Mission.objects.get(id=self.kwargs['id'])
        except mission.DoesNotExist:
            return Tag.objects.none()

        tag_ids = Mission_tags.objects.filter(mission=mission).values_list('tag_id', flat=True)
        return  Tag.objects.filter(id__in=tag_ids)

"""
update db:
python manage.py makemigrations
python manage.py migrate

start server
python manage.py runserver
"""
