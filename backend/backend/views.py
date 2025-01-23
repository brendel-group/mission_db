from typing import Iterable
from django.http import StreamingHttpResponse, HttpResponse, HttpRequest, FileResponse
from restapi.models import File as FileModel
from django.core.files import File
from django.core.files.storage import Storage
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.conf import settings
import os
import random
import string


def authenticate(sessionid: str):
    try:
        session = Session.objects.get(session_key=sessionid)
    except Session.DoesNotExist:
        raise PermissionDenied

    session_data = session.get_decoded()
    uid = session_data.get("_auth_user_id")
    user = User.objects.get(id=uid)

    if not user.is_authenticated:
        raise PermissionDenied

    return user


def download(request: HttpRequest, file_path: str):
    # try to find user by sessionid
    if not settings.DEBUG:
        _ = authenticate(request.GET["sessionid"])

    storage: Storage = FileModel.file.field.storage
    try:
        file = storage.open(file_path)
    except (FileNotFoundError, IsADirectoryError):
        return HttpResponse(f"File not found: {file_path}", status=404)

    if "range" in request.headers:
        return _range_download(request, file)

    response = FileResponse(file)
    response["Content-Disposition"] = (
        f'attachement; filename="{os.path.basename(file.name)}"'
    )
    response["Accept-Ranges"] = "bytes"
    response["Content-Length"] = file.size
    return response


def _extract_ranges(range_header: str, file_size: int):
    ranges = range_header.split(",")
    new_ranges = []
    for r in ranges:
        r = r.split("-")
        if r[0] and r[1]:
            r = range(int(r[0]), int(r[1]) + 1)
        elif r[0]:
            r = range(int(r[0]), file_size)
        elif r[1]:
            r = range(file_size - int(r[1]), file_size)
        new_ranges.append(r)
    return new_ranges


def _range_download(request: HttpRequest, file: File):
    if "bytes" in request.headers["range"]:
        range_header: str = (
            request.headers["range"].replace("bytes=", "").replace(" ", "")
        )
    else:
        return HttpResponse(status=400)

    ranges: list[range] = _extract_ranges(range_header, file.size)

    if not ranges:
        return HttpResponse(status=400)

    for r in ranges:
        if r.start < 0 or r.stop > file.size:
            return HttpResponse(status=416)

    if len(ranges) > 1:
        return _multipart_range_download(ranges, file)

    # continue with single part range

    requested_range = ranges[0]

    range_size = len(requested_range)

    response = StreamingHttpResponse(
        streaming_content=_chunk_generator(file, requested_range, close=True),
        status=206,
    )

    response["content-type"] = "Content-Type: application/octet-stream"
    response["content-length"] = range_size
    response["content-range"] = (
        f"bytes {requested_range.start}-{requested_range.stop-1}/{file.size}"
    )

    return response


def _multipart_range_download(ranges: list[range], file: File):
    range_sizes: list[int] = [len(r) for r in ranges]

    content_length: int = sum(range_sizes)

    body: list[Iterable[bytes]] = []

    # generate random 13 digit string of letters and digits
    boundary: str = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=13)
    )

    for r in ranges:
        # add header for multipart body
        body.append(
            [
                f"\r\n--{boundary}\r\n",
                "Content-Type: application/octet-stream\r\n",
                f"Content-Range: bytes {r.start}-{r.stop-1}/{file.size}\r\n",
            ]
        )
        content_length += sum([len(c) for c in body[-1]])

        # add content
        body.append(_chunk_generator(file, r))

    # add indicator for end
    body.append([f"\r\n--{boundary}--\r\n"])
    content_length += sum([len(c) for c in body[-1]])

    response = StreamingHttpResponse(
        streaming_content=_body_generator(file, body, boundary), status=206
    )

    # set required headers
    response["Content-Disposition"] = (
        f'attachement; filename="{os.path.basename(file.name)}"'
    )
    response["Accept-Ranges"] = "bytes"

    response["Content-Type"] = f"multipart/byteranges; boundary={boundary}"
    response["Content-Length"] = content_length
    return response


def _chunk_generator(
    file: File, r: range, chunk_size: int = File.DEFAULT_CHUNK_SIZE, close: bool = False
):
    try:
        file.seek(r.start)
        for i in range(int(len(r) / chunk_size)):
            yield file.read(chunk_size)

        # last chunk may be smaller than chunk_size
        last_chunk = r.stop - file.tell()
        if last_chunk > 0:
            yield file.read(last_chunk)
    finally:
        if close:
            file.close()


def _body_generator(file: File, body: list[Iterable[bytes]], boundary: str):
    for chunks in body:
        for chunk in chunks:
            if chunk == f"\r\n--{boundary}--\r\n":
                file.close()
            yield chunk


def stream(request):
    file = File.objects.first().file
    response = StreamingHttpResponse(streaming_content=file.chunks())
    return response
