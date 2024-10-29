from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Mission
from .serializer import MissionSerializer

@api_view(["GET"])
def get_mission(request):
    return Response(MissionSerializer({'id': 0, 
                                       'name': 'picking apples', 
                                       'date': '2024-10-29 14:58:33.732505',
                                       'location': 'Tuebingen',
                                       'other': ''}).data)



'''
id = models.IntegerField()
    name = models.CharField(max_length=1000) # TODO: what should max_length be?
    date = models.DateTimeField()
    location = models.CharField(max_length=1000)
    other = models.CharField()
'''