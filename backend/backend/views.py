from django.http import StreamingHttpResponse
from restapi.models import File


def download(request):
    file = File.objects.first().file
    response = StreamingHttpResponse(streaming_content=file.chunks())
    response["Content-Disposition"] = f'attachement; filename="{file.name}"'
    return response


def stream(request):
    file = File.objects.first().file
    response = StreamingHttpResponse(streaming_content=file.chunks())
    return response
