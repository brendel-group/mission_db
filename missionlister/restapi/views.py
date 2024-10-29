from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Mission
from .serializer import MissionSerializer

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

'''
id = models.IntegerField()
    name = models.CharField(max_length=1000) # TODO: what should max_length be?
    date = models.DateTimeField()
    location = models.CharField(max_length=1000)
    other = models.CharField()
'''