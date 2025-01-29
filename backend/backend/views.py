from typing import Iterable
from django.http import StreamingHttpResponse, HttpResponse, HttpRequest, FileResponse
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.conf import settings
import os
import random
import string


def authenticate(sessionid: str):
    """
    Takes a sessionid as string a confirms the session exists and the user is authenticated

    Args:
        sessionid (str): sessionid as in the sessionid cookie or session_key in the database

    Raises:
        PermissionDenied: when session does not exist or user not authenticated

    Returns:
        User: The user associated with the session
    """
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
    """
    View that handles downloads. Can handle complete file, single-part and multi-part range requests.

    Args:
        request (HttpRequest): http request optionally containing a range header and sessionid as url parameter
        file_path (str): The requested file

    Returns:
        403 Response: if session not found or user not authenticated
        404 Response: if file not found
        200 Response: if whole file requested. Contains the whole file as bytes
        201 Response: if range requested. A single-part range contains the requested byte range as body.
            A multi part range has a MimeType multipart body which consists of multiple parts with their own headers.\\
            The bodies of these parts are the requested byte ranges
    """
    # try to find user by sessionid
    if not settings.DEBUG:
        try:
            sessionid = request.GET["sessionid"]
        except Exception:
            raise PermissionDenied
        _ = authenticate(sessionid)

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
    """Parses the range header and converts the ranges to python ranges
    Note: ranges in header are inclusive while python ranges are not inclusive on the upper bound

    Args:
        range_header (str): content of range header as string
        file_size (int): the maximum file size

    Returns:
        list[range]: List of the extracted ranges
    """
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
    """Handles downloads if a range is requested

    Args:
        request (HttpRequest): The original request with the range header
        file (File): The requested file

    Returns:
        201 Response: The requested byte ranges. Either as single range or multipart response with multiple ranges.
    """
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
        f"bytes {requested_range.start}-{requested_range.stop - 1}/{file.size}"
    )

    return response


def _multipart_range_download(ranges: list[range], file: File):
    """Handles multipart range requests\\
    The response consists of multiple parts which each having their own headers and bodies.\\
    The parts are separated by a boundary that is declared in the main headers.\\
    The boundary is a random 13 digit string

    Args:
        ranges (list[range]): requested ranges
        file (File): requested file

    Returns:
        201 Response: The mutlipart response with the different byte ranges.
    """
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
                f"Content-Range: bytes {r.start}-{r.stop - 1}/{file.size}\r\n",
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
    """Takes a file and range and acts as an iterator that reads the file in chunks until the end of the range is reached.\\
    Starts reading tha file at the start of the range and not the start of the file.\\
    Optionally can close the file after reading the last chunk.

    Args:
        file (File): The file from which to read
        r (range): The range in bytes to read.
        chunk_size (int, optional): The size of chunks in which the file will be read. Defaults to File.DEFAULT_CHUNK_SIZE.
        close (bool, optional): Close the file after reading last chunk. Defaults to False.

    Yields:
        chunk_size large byte blocks read from the file
    """
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
    """Takes the body of the multipart range response as a list of iterators and acts like a single iterator,\\
    so that this can be passed to the StreamingHttpResponse.\\
    Closes the file when the last boundary is reached.    

    Args:
        file (File): The opened file to close it at the end.
        body (list[Iterable[bytes]]): The body as list of iterators.
        boundary (str): The boundary separating the multipart bodies. To check when the end is reached.

    Yields:
        The body parts either line by line (header) or in byte blocks.
    """
    for chunks in body:
        for chunk in chunks:
            if chunk == f"\r\n--{boundary}--\r\n":
                file.close()
            yield chunk


def stream(request: HttpRequest, file_path: str):
    response = download(request, file_path)
    if "content-disposition" in response:
        del response["Content-Disposition"]
    response["X-Frame-Options"] = ""
    return response
