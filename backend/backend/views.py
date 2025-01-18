from django.http import StreamingHttpResponse, HttpResponse, HttpRequest
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
    except FileNotFoundError:
        return HttpResponse(status=404)

    if "range" in request.headers:
        return _range_download(request, file)

    response = StreamingHttpResponse(streaming_content=file.chunks())
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


def _range_download(request: HttpRequest, file: File):
    if "bytes" in request.headers["range"]:
        range_header: str = (
            request.headers["range"].replace("bytes=", "").replace(" ", "")
        )
    else:
        return HttpResponse(status=400)

    multipart_ranges: list[range] = _extract_ranges(range_header)

    range_sizes = [len(r) for r in multipart_ranges]

    content_length = sum(range_sizes)

    chunk_size = range_sizes[0]
    for size in range_sizes:
        chunk_size = math.gcd(chunk_size, size)

    chunk_ranges = map(
        lambda r: range(int(r.start / chunk_size), int(r.stop / chunk_size)),
        multipart_ranges,
    )

    chunks: list[iter[bytes]] = []

    boundary = "".join(random.choices(string.ascii_lowercase + string.digits, k=13))

    for r in chunk_ranges:
        chunks.append(
            (
                f"\r\n--{boundary}\r\n",
                f"Content-Range: bytes {r.start*chunk_size}-{r.stop*chunk_size}/{file.size}\r\n",
            )
        )
        content_length += sum([len(c) for c in chunks[-1]])
        file.seek(r.start * chunk_size)
        chunks.append(itertools.islice(file.chunks(chunk_size), len(r)))

    chunks.append((f"\r\n--{boundary}--\r\n"))
    content_length += sum([len(c) for c in chunks[-1]])

    chunks_iter: iter[bytes] = iter([])
    for chunk in chunks:
        chunks_iter = itertools.chain(chunks_iter, chunk)

    response = StreamingHttpResponse(streaming_content=chunks_iter, status=206)
    response["Content-Disposition"] = (
        f'attachement; filename="{os.path.basename(file.name)}"'
    )
    response["Accept-Ranges"] = "bytes"

    response["Content-Type"] = f"multipart/byteranges, boundary={boundary}"
    response["Content-Length"] = content_length
    return response


def stream(request):
    file = File.objects.first().file
    response = StreamingHttpResponse(streaming_content=file.chunks())
    return response
