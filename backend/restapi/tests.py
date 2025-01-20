from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.storage.memory import InMemoryStorage
from django.core.files.base import ContentFile
from .models import Tag, Mission, Mission_tags, File, Mission_files
import logging
import urllib.parse

# user without password for tests
user: User = User(username="test")


class APIAuthTestCase(APITestCase):
    def setUp(self):
        global user
        if not User.objects.filter(username=user.username).exists():
            user.save()

        # login the user even without password (faster, because skips hashing)
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()


class RestApiPostMissionTestCase(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        self.firstMission = Mission.objects.create(
            name="TestMission",
            date="2024-10-29",
            location="TestLocation",
            notes="TestOther",
        )
        self.secondMission = Mission.objects.create(
            name="TestMission2",
            date="2024-10-29",
            location="TestLocation2",
            notes="TestOther2",
        )

    def tearDown(self):
        super().tearDown()

    def test_get_missions(self):
        response = self.client.get(
            reverse("get_missions"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data[0],
            {
                "id": self.firstMission.id,
                "name": "TestMission",
                "date": "2024-10-29",
                "location": "TestLocation",
                "notes": "TestOther",
            },
        )
        self.assertEqual(
            response.data[1],
            {
                "id": self.secondMission.id,
                "name": "TestMission2",
                "date": "2024-10-29",
                "location": "TestLocation2",
                "notes": "TestOther2",
            },
        )

    def test_get_by_id(self):
        response = self.client.get(
            reverse("mission_detail", kwargs={"pk": self.firstMission.id}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": self.firstMission.id,
                "name": "TestMission",
                "date": "2024-10-29",
                "location": "TestLocation",
                "notes": "TestOther",
            },
        )

    def test_put_by_id(self):
        response = self.client.put(
            reverse("mission_detail", kwargs={"pk": self.firstMission.id}),
            {
                "name": "TestMissionUpdated",
                "date": "2024-10-29",
                "location": "TestLocation",
                "notes": "TestOther",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": self.firstMission.id,
                "name": "TestMissionUpdated",
                "date": "2024-10-29",
                "location": "TestLocation",
                "notes": "TestOther",
            },
        )

    def test_delete_by_id(self):
        response = self.client.delete(
            reverse("mission_detail", kwargs={"pk": self.secondMission.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Mission.objects.filter(id=self.secondMission.id)), 0)


class TagTestCase(TestCase):
    test_names = list()

    def setUp(self):
        test_number = list(range(0, 5))
        for n in test_number:
            while Tag.objects.filter(name="test" + str(n)).exists():
                n += 1
            Tag.objects.create(name="test" + str(n))
            self.test_names.append("test" + str(n))

    def test_structure(self):
        self.assertEqual(
            len(Tag.objects.filter(name__in=self.test_names)),
            5,
            "Test if 5 tags where created",
        )

    def test_unique_violation(self):
        # use an existing name
        name = self.test_names[0]

        # and a new id
        id = Tag.objects.get(name=name).id + 1
        while Tag.objects.filter(id=id).exists():
            id += 1

        # should raise an exception because name is unique
        self.assertRaises(IntegrityError, Tag.objects.create, id=id, name=name)


class RestAPITagTestCase(APIAuthTestCase):
    test_names = list()

    def setUp(self):
        super().setUp()
        test_number = list(range(0, 5))
        for n in test_number:
            while Tag.objects.filter(name="test" + str(n)).exists():
                n += 1
            Tag.objects.create(name="test" + str(n))
            self.test_names.append("test" + str(n))

        # raise logging level to ERROR
        logger = logging.getLogger("django.request")
        self.previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def tearDown(self):
        super().tearDown()
        # reset logigng level
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_logging_level)

    def test_get_tags(self):
        response = self.client.get(
            reverse("get_tags"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(
            response.data,
            [
                {
                    "id": Tag.objects.get(name=self.test_names[0]).id,
                    "name": self.test_names[0],
                    "color": "#FFFFFF",
                },
                {
                    "id": Tag.objects.get(name=self.test_names[1]).id,
                    "name": self.test_names[1],
                    "color": "#FFFFFF",
                },
                {
                    "id": Tag.objects.get(name=self.test_names[2]).id,
                    "name": self.test_names[2],
                    "color": "#FFFFFF",
                },
                {
                    "id": Tag.objects.get(name=self.test_names[3]).id,
                    "name": self.test_names[3],
                    "color": "#FFFFFF",
                },
                {
                    "id": Tag.objects.get(name=self.test_names[4]).id,
                    "name": self.test_names[4],
                    "color": "#FFFFFF",
                },
            ],
        )

    def test_create_tag_only_name(self):
        response = self.client.post(
            reverse("create_tag"),
            {"name": "test_create_tag"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            response.data,
            {
                "id": Tag.objects.get(name="test_create_tag").id,
                "name": "test_create_tag",
                "color": "#FFFFFF",
            },
        )

    def test_create_tag(self):
        response = self.client.post(
            reverse("create_tag"),
            {"name": "test_create_tag2", "color": "#00FF00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(
            response.data,
            {
                "id": Tag.objects.get(name="test_create_tag2").id,
                "name": "test_create_tag2",
                "color": "#00FF00",
            },
        )

    def test_create_tag_with_existing_name(self):
        existing_name = self.test_names[0]
        response = self.client.post(
            reverse("create_tag"),
            {"name": existing_name},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"name": ["tag with this name already exists."]}
        )

    def test_tag_detail_get(self):
        response = self.client.get(
            reverse("tag_detail", kwargs={"name": self.test_names[0]}),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": Tag.objects.get(name=self.test_names[0]).id,
                "name": self.test_names[0],
                "color": "#FFFFFF",
            },
        )

    def test_tag_detail_put(self):
        response = self.client.put(
            reverse("tag_detail", kwargs={"name": self.test_names[0]}),
            {"name": "test_detail_put"},
            format="json",
        )
        self.test_names[0] = "test_detail_put"
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": Tag.objects.get(name="test_detail_put").id,
                "name": "test_detail_put",
                "color": "#FFFFFF",
            },
        )

    def test_tag_detail_delete(self):
        response = self.client.delete(
            reverse("tag_detail", kwargs={"name": self.test_names[0]}),
        )
        del self.test_names[0]
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RestAPIMissionTagsTestCase(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        # Create test data
        self.mission = Mission.objects.create(
            name="TestMission",
            date=timezone.now(),
            location="TestLocation",
            notes="TestOther",
        )
        self.tags = []
        for i in range(3):
            tag = Tag.objects.create(name=f"TestTag{i}")
            self.tags.append(tag)

        # Create initial tag associations
        self.mission_tag = Mission_tags.objects.create(
            mission=self.mission, tag=self.tags[0]
        )

    def tearDown(self):
        super().tearDown()

    def test_add_tag_to_mission(self):
        # Add a new tag to a mission using the API
        data = {"mission_id": self.mission.id, "tag_name": "TestTag4"}
        response = self.client.post(
            reverse("add_tag_to_mission"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if the mission is now associated with the new tag
        tag = Tag.objects.get(name="TestTag4")
        self.assertTrue(
            Mission_tags.objects.filter(mission=self.mission, tag=tag).exists()
        )

        # Add an exsiting tag to confirm different status code
        data = {"mission_id": self.mission.id, "tag_name": "TestTag1"}
        response = self.client.post(
            reverse("add_tag_to_mission"),
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_mission_tag(self):
        # Remove tag association using the API
        response = self.client.delete(
            reverse(
                "delete_mission_tag",
                kwargs={"mission_id": self.mission.id, "tag_name": self.tags[0].name},
            ),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check if the mission-tag association is removed
        self.assertFalse(
            Mission_tags.objects.filter(mission=self.mission, tag=self.tags[0]).exists()
        )

    def test_get_missions_by_tag(self):
        # Check missions related to a specific tag
        response = self.client.get(
            reverse("get_missions_by_tag", kwargs={"name": "TestTag0"}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.mission.id)

    def test_get_tags_by_mission_id(self):
        # Check tags associated with a mission
        response = self.client.get(
            reverse("get_tags_by_mission_id", kwargs={"id": self.mission.id}),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.tags[0].name)


class MissionTagCascadeDeleteTests(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        # Create a mission and some tags
        self.mission1 = Mission.objects.create(name="TestMission", date=timezone.now())
        self.mission2 = Mission.objects.create(name="TestMission2", date=timezone.now())
        self.tag1 = Tag.objects.create(name="TestTag1")
        self.tag2 = Tag.objects.create(name="TestTag2")

        # Create mission-tag relationships
        self.mission_tag1 = Mission_tags.objects.create(
            mission=self.mission1, tag=self.tag1
        )
        self.mission_tag2 = Mission_tags.objects.create(
            mission=self.mission2, tag=self.tag2
        )

    def tearDown(self):
        super().tearDown()

    def test_mission_deletes_mission_tags(self):
        self.mission1.delete()
        self.mission1.save()
        mission_tags_exist = Mission_tags.objects.filter(mission=self.mission1).exists()
        self.assertFalse(mission_tags_exist)

    def test_tag_deletes_mission_tags(self):
        self.tag2.delete()
        self.tag2.save()
        mission_tags_exist = Mission_tags.objects.filter(tag=self.tag2).exists()
        self.assertFalse(mission_tags_exist)


class NotFoundErrors(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        self.mission = Mission.objects.create(name="TestMission", date=timezone.now())
        self.tag = Tag.objects.create(name="test tag")

        # raise logging level to ERROR
        logger = logging.getLogger("django.request")
        self.previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def tearDown(self):
        super().tearDown()
        # reset logigng level
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_logging_level)

    def test_tag_detail_not_found(self):
        response = self.client.get(
            reverse("tag_detail", kwargs={"name": "notfound"}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_mission_tag(self):
        # Tag not found
        response = self.client.delete(
            reverse(
                "delete_mission_tag",
                kwargs={"mission_id": self.mission.id, "tag_name": "notfound"},
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Tag not found."})

        # Misison not found
        response = self.client.delete(
            reverse(
                "delete_mission_tag",
                kwargs={"mission_id": self.mission.id + 1, "tag_name": "test tag"},
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Mission not found."})

        # Mission-tag not found
        response = self.client.delete(
            reverse(
                "delete_mission_tag",
                kwargs={"mission_id": self.mission.id, "tag_name": "test tag"},
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Mission_tags entry not found."})

    def test_get_missions_by_tag(self):
        response = self.client.get(
            reverse("get_missions_by_tag", kwargs={"name": "notfound"}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Tag with name notfound not found"})

    def test_get_tags_by_mission(self):
        response = self.client.get(
            reverse("get_tags_by_mission_id", kwargs={"id": self.mission.id + 1}),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data,
            {"detail": f"Mission with id {self.mission.id + 1} not found"},
        )

    def test_create_mission_tag(self):
        response = self.client.post(
            reverse("add_tag_to_mission"),
            {"mission_id": self.mission.id + 1, "tag_name": "test tag"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data,
            {"detail": f"Mission with id {self.mission.id + 1} not found"},
        )

    def test_get_files_by_nonexistent_mission(self):
        response = self.client.get(
            reverse("get_files_by_mission_id", kwargs={"mission_id": 999}),
        )  # Nonexistent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "Mission with ID 999 not found"})


class MissionFilesTestCase(APIAuthTestCase):
    def setUp(self):
        # fake storage
        self._field = File.file.field
        self._default_storage = self._field.storage
        test_storage = InMemoryStorage()
        self._field.storage = test_storage

        # create files
        file_content = ContentFile("")
        test_storage.save("path/to/file1", file_content)
        test_storage.save("path/to/file2", file_content)

        super().setUp()
        # Create a mission
        self.mission = Mission.objects.create(
            name="TestMission",
            date=timezone.now(),
            location="TestLocation",
            notes="TestOther",
        )

        # Create files
        self.file1 = File.objects.create(
            id=0,
            file="path/to/file1",
            robot="TestRobot1",
            duration=12000,
            size=1024,
        )
        self.file2 = File.objects.create(
            id=1,
            file="path/to/file2",
            robot="TestRobot2",
            duration=24000,
            size=2048,
        )

        # Associate files with the mission
        Mission_files.objects.create(mission=self.mission, file=self.file1)
        Mission_files.objects.create(mission=self.mission, file=self.file2)

    def tearDown(self):
        super().tearDown()
        self._field.storage = self._default_storage

    def test_get_files_by_mission(self):
        response = self.client.get(
            reverse("get_files_by_mission_id", kwargs={"mission_id": self.mission.id}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Expecting 2 files associated with the mission
        self.assertEqual(response.data[0]["file"]["id"], self.file1.id)
        self.assertEqual(response.data[1]["file"]["id"], self.file2.id)


class SpecialTagNameTest(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        self.tag = Tag(name="create/")
        self.tag.full_clean()
        self.tag.save()
        self.encoded_name = urllib.parse.quote_plus(
            self.tag.name
        )  # tests don't use the webserver so no double encoding needed

    def tearDown(self):
        super().tearDown()

    def test_create_other_tag(self):
        response = self.client.post(
            reverse("create_tag"),
            {"name": "test"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tag.objects.filter(name="test").exists())

    def test_change_tag(self):
        response = self.client.put(
            reverse("tag_detail", kwargs={"name": self.encoded_name}),
            {"name": "create/", "color": "#ff0000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.color, "#ff0000")

    def test_delete_tag(self):
        response = self.client.delete(
            reverse("tag_detail", kwargs={"name": self.encoded_name}),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(name="create/").exists())
