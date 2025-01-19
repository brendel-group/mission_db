from functools import reduce
from typing import Iterable
from django.http import StreamingHttpResponse, HttpResponse, HttpRequest, FileResponse
from restapi.models import File as FileModel
from django.core.files import File
from django.core.files.storage import Storage
import os
import math
import itertools
import random
import string


def download(request: HttpRequest, file_path: str):
    # file = File.objects.first().file
    storage: Storage = FileModel.file.field.storage
    try:
        file = storage.open(file_path)
    except (FileNotFoundError, IsADirectoryError):
        return HttpResponse(f"File not {file_path}", status=404)

    if "range" in request.headers:
        return _range_download(request, file)

    response = FileResponse(file)
    response["Content-Disposition"] = (
        f'attachement; filename="{os.path.basename(file.name)}"'
    )
    response["Accept-Ranges"] = "bytes"
    response["Content-Length"] = file.size
    return response


def _extract_ranges(range_header: str):
    ranges = range_header.split(",")
    new_ranges = []
    for r in ranges:
        r = r.split("-")
        r = range(int(r[0]), int(r[1]))
        new_ranges.append(r)
    return new_ranges


def _gcd_below_max(integers: list[int], max_value: int) -> int:
    # calculate greatest common divisor
    gcd = reduce(math.gcd, integers)

    if gcd <= max_value:
        return gcd

    # find common divisor that is smaller than max_value
    for i in range(max_value, 0, -1):
        if gcd % i == 0:
            return i


def _range_download(request: HttpRequest, file: File):
    if "bytes" in request.headers["range"]:
        range_header: str = (
            request.headers["range"].replace("bytes=", "").replace(" ", "")
        )
    else:
        return HttpResponse(status=400)

    ranges: list[range] = _extract_ranges(range_header)

    range_sizes: list[int] = [len(r) for r in ranges]

    content_length: int = sum(range_sizes)

    chunk_size: int = _gcd_below_max(range_sizes, File.DEFAULT_CHUNK_SIZE)

    range_sizes: list[int] = [int(size / chunk_size) for size in range_sizes]

    body: list[Iterable[bytes]] = []

    # generate random 13 digit string of letters and digits
    boundary: str = "".join(
        random.choices(string.ascii_lowercase + string.digits, k=13)
    )

    for size, r in zip(range_sizes, ranges):
        # add header for multipart body
        body.append(
            [
                f"\r\n--{boundary}\r\n",
                "Content-Type: application/octet-stream\r\n",
                f"Content-Range: bytes {r.start}-{r.stop}/{file.size}\r\n",
            ]
        )
        content_length += sum([len(c) for c in body[-1]])

        # add content
        file.seek(r.start)
        body.append(itertools.islice(file.chunks(chunk_size), size))

    # add indicator for end
    body.append([f"\r\n--{boundary}--\r\n"])
    content_length += sum([len(c) for c in body[-1]])

    response = StreamingHttpResponse(
        streaming_content=_body_generator(file, body), status=206
    )

    # set required headers
    response["Content-Disposition"] = (
        f'attachement; filename="{os.path.basename(file.name)}"'
    )
    response["Accept-Ranges"] = "bytes"

    response["Content-Type"] = f"multipart/byteranges; boundary={boundary}"
    response["Content-Length"] = content_length
    return response


def _body_generator(file: File, body: list[Iterable[bytes]]):
    try:
        for iterable in body:
            for chunk in iterable:
                yield chunk
    finally:
        file.close()


def stream(request):
    file = File.objects.first().file
    response = StreamingHttpResponse(streaming_content=file.chunks())
    return response
