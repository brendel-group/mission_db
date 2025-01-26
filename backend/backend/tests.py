from django.test import TestCase
import backend.views
from backend.views import _chunk_generator
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.files.base import ContentFile
from django.core.files.storage.memory import InMemoryStorage
from django.http import FileResponse, StreamingHttpResponse
from restapi.models import File
from unittest.mock import patch


# user without password for tests
user: User = User(username="test")


class FileDownloadTest(TestCase):
    def setUp(self):
        global user
        if not User.objects.filter(username=user.username).exists():
            user.save()

        # login the user even without password (faster, because skips hashing)
        self.client.force_login(user=user)

        # Fake storage
        self._default_storage = backend.views.storage
        test_storage = InMemoryStorage()
        backend.views.storage = test_storage
        File.file.field.storage = test_storage

        # create files
        file_content = ContentFile("12345678901", "path/to/file.test")
        test_storage.save(file_content.name, file_content)

        file = File.objects.create(file=file_content.name, size=123, duration=123)
        self.file = file.file

        # override _chunk_generator to force smaller chunk_size (5)
        self._chunk_generator_patcher = patch(
            "backend.views._chunk_generator",
            side_effect=lambda file,
            r,
            chunk_size=backend.views.File.DEFAULT_CHUNK_SIZE,
            close=False: _chunk_generator(file, r, 5, close),
        )
        self._chunk_generator_patcher.start()

    def tearDown(self):
        self.client.logout()
        backend.views.storage = self._default_storage
        File.file.field.storage = self._default_storage
        self._chunk_generator_patcher.stop()

    def test_whole_file_download(self):
        response: FileResponse = self.client.get(
            reverse("download", kwargs={"file_path": self.file.name})
            + f"?sessionid={Session.objects.first().session_key}"
        )
        self.assertEqual(b"".join(response.streaming_content), self.file.open().read())

    def test_single_range_download(self):
        file_content = self.file.open().read()
        self.file.close()

        # range with start and end
        response: StreamingHttpResponse = self.client.get(
            reverse("download", kwargs={"file_path": self.file.name})
            + f"?sessionid={Session.objects.first().session_key}",
            headers={
                "range": "bytes=0-5",
            },
        )
        self.assertEqual(b"".join(response.streaming_content), file_content[:6])

        # range without start (last 5 bytes)
        response: StreamingHttpResponse = self.client.get(
            reverse("download", kwargs={"file_path": self.file.name})
            + f"?sessionid={Session.objects.first().session_key}",
            headers={
                "range": "bytes=-5",
            },
        )
        content = b"".join(response.streaming_content)
        self.assertEqual(content, file_content[-5:])

        # range without end (read from start till end of file)
        response: StreamingHttpResponse = self.client.get(
            reverse("download", kwargs={"file_path": self.file.name})
            + f"?sessionid={Session.objects.first().session_key}",
            headers={
                "range": "bytes=5-",
            },
        )
        self.assertEqual(b"".join(response.streaming_content), file_content[5:])

    def test_multi_range_download(self):
        response: StreamingHttpResponse = self.client.get(
            reverse("download", kwargs={"file_path": self.file.name})
            + f"?sessionid={Session.objects.first().session_key}",
            headers={
                "range": "bytes=6-,4-9",
            },
        )
        body = list(response.streaming_content)
        boundary: bytes = str.encode(response.headers.get("content-type").split("=")[1])
        body_parts: list[list[bytes]] = []
        for line in body:
            if boundary in line:
                body_parts.append([])
                continue
            body_parts[-1].append(line)
        del body_parts[-1]

        contents: list[list[bytes]] = []
        for part in body_parts:
            contents.append([])
            for line in part:
                if b"Content-Type:" in line or b"Content-Range" in line:
                    # ignore additonal header fields
                    continue

                contents[-1].append(line)

        self.assertEqual(len(contents), 2)
        self.assertEqual(len(contents[0]), 1)
        self.assertEqual(len(contents[1]), 2)

        file = self.file.open()
        file.seek(6)
        self.assertEqual(contents[0][0], file.read())
        file.seek(4)
        # second range should be split in two parts because of chunk_size=5
        self.assertEqual(contents[1][0], file.read(5))
        self.assertEqual(contents[1][1], file.read(1))
        file.close()
