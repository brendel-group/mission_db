from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework import status
from .models import (
    Denied_topics,
    File,
    Tag,
    Mission,
    Mission_tags,
    Topic,
)
from .serializer import (
    DeniedTopicNameSerializer,
    FileSerializer,
    TagSerializer,
    MissionSerializer,
    MissionWasModifiedSerializer,
    MissionTagSerializer,
    TopicSerializer,
)
import urllib.parse


@api_view(["GET"])
def get_missions(request):
    missions = Mission.objects.all()
    serializer = MissionSerializer(missions, many=True)
    return Response(serializer.data)


@api_view(["PUT"])
def set_was_modified(request, pk):
    try:
        mission = Mission.objects.get(pk=pk)
    except Mission.DoesNotExist:
        return Response(
            {"error": "Mission not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = MissionWasModifiedSerializer(
        instance=mission, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    except Mission.DoesNotExist:
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


@api_view(["GET"])
def get_files_by_mission_id(request, mission_id):
    """
    List all files with type of a mission by ID
    ### Returns
    Response with list of files with type in json format\
    Or NotFound exception
    """
    try:
        mission = Mission.objects.get(id=mission_id)
    except Mission.DoesNotExist:
        raise NotFound(f"Mission with ID {mission_id} not found")
    files = File.objects.filter(mission=mission)
    serializer = FileSerializer(files, many=True, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_file_by_path(request, file_path: str):
    """
    Get info about one file
    ### Returns
    A json containing info about a file
    Or 404 Not found if the requested file does not exist
    """
    try:
        file = File.objects.get(file=file_path)
    except File.DoesNotExist:
        raise NotFound(f"No such file: {file_path}")

    serializer = FileSerializer(file, context={"request": request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_topics_from_files(request, file_path):
    """
    List all topics of a file
    ### Returns
    Response with list of topics in json format
    """
    try:
        file = File.objects.get(file=file_path)
    except File.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    topics = Topic.objects.filter(file=file)
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def denied_topics(request):
    """
    List all denied topic names
    ### Returns
    List of denied topic names in json format
    """
    topic_names = Denied_topics.objects.all()
    serializer = DeniedTopicNameSerializer(topic_names, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def denied_topics_create(request):
    """
    Creates a new denied topic name
    ### Parameters
    request: POST Request containing name of the denied topic name
    ### Returns
    Response with data of created denied topic name object containing name\
    Or HTTP_400_BAD_REQUEST Response
    """
    serializer = DeniedTopicNameSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def denied_topics_delete(request, name):
    """
    Delete an denied topic name
    ### Parameters
    name: name of the denied topic name
    ### Returns
    success response or
    HTTP_404_NOT_FOUND if denied topic name not found
    """
    name = urllib.parse.unquote(name)
    try:
        denied_topic_name = Denied_topics.objects.get(name=name)
    except Denied_topics.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    denied_topic_name.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def get_tags(request):
    """
    List all tags in database
    ### Returns
    List of tags in json format as ResponseFileByMissionAPI,
    """
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def create_tag(request):
    """
    Create new tag
    ### Parameters
    request: POST Request containing tag name and optionally a hex color in json format
    ### Returns
    Response with data of created tag object containing id, name and color\
    Or HTTP_400_BAD_REQUEST Response
    """
    serializer = TagSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def tag_detail(request, name):
    """
    Alter a tag or get data
    ### Parameters
    request: GET, PUT or DELETE request.
    PUT request has to contain updated data of Tag
    ### Returns
    Tag data or HTTP error in Response
    """
    name = urllib.parse.unquote(name)
    try:
        tag = Tag.objects.get(name=name)
    except Tag.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MissionByTagAPI(generics.ListAPIView):
    serializer_class = MissionSerializer
    name = "Get Missions by Tag"

    def get_queryset(self):
        """
        Lists Missions that have a Tag with a given name
        ### Returns
        Missions list
        ### Raises
        NotFound if Tag with given name not found
        """
        name = urllib.parse.unquote(self.kwargs["name"])
        try:
            tag = Tag.objects.get(name=name)
        except Tag.DoesNotExist:
            raise NotFound(f"Tag with name {self.kwargs['name']} not found")
        mission_ids = Mission_tags.objects.filter(tag=tag).values_list(
            "mission_id", flat=True
        )
        return Mission.objects.filter(id__in=mission_ids)


class TagByMissionAPI(generics.ListAPIView):
    serializer_class = TagSerializer
    name = "Get Tags by Mission id"

    def get_queryset(self):
        """
        List Tags of a Mission
        ### Returns
        List of Tags
        ### Raises
        NotFound if no Mission with given id exists
        """
        try:
            mission = Mission.objects.get(id=self.kwargs["id"])
        except Mission.DoesNotExist:
            raise NotFound(f"Mission with id {self.kwargs['id']} not found")
        tag_ids = Mission_tags.objects.filter(mission=mission).values_list(
            "tag_id", flat=True
        )
        return Tag.objects.filter(id__in=tag_ids)


@api_view(["POST"])
def add_tag_to_mission(request):
    """
    Assign/add a tag to a misison
    Will create a new tag when no tag with that name was found
    ### Parameters
    request: POST Request containing mission_id and tag_name
    ### Returns
    json with given mission_id and tag_name
    ### Response codes
    HTTP_201_CREATED when a new tag was created\\
    HTTP_200_OK\\
    HTTP_400_BAD_REQUEST\\
    HTTP_404_NOT_FOUND
    """
    serializer = MissionTagSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        if serializer.tag_created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_mission_tag(request, mission_id, tag_name):
    """
    Delete a tag from a mission
    ### Parameters
    request: DELETE request with no data\\
    mission_id: Mission id\\
    tag_name: name of Tag
    ### Returns
    success response or
    HTTP_404_NOT_FOUND if mission, tag or relation not found
    """
    tag_name = urllib.parse.unquote(tag_name)
    try:
        # Retrieve the mission using the mission_id
        mission = Mission.objects.get(id=mission_id)
    except Mission.DoesNotExist:
        return Response(
            {"error": "Mission not found."}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Retrieve the tag using the tag_name
        tag = Tag.objects.get(name=tag_name)
    except Tag.DoesNotExist:
        return Response({"error": "Tag not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Find the Mission_tags entry
        mission_tag = Mission_tags.objects.get(mission=mission, tag=tag)
    except Mission_tags.DoesNotExist:
        return Response(
            {"error": "Mission_tags entry not found."}, status=status.HTTP_404_NOT_FOUND
        )

    # Delete the Mission_tags entry
    mission_tag.delete()
    return Response(
        {"success": "Mission_tags entry deleted."}, status=status.HTTP_204_NO_CONTENT
    )
