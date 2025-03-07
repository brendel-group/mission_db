from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.storage.memory import InMemoryStorage
from django.core.files.base import ContentFile
from .models import (
    Denied_topics,
    Tag,
    Mission,
    Mission_tags,
    File,
    Topic,
)
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
            was_modified=False,
        )
        self.secondMission = Mission.objects.create(
            name="TestMission2",
            date="2024-10-29",
            location="TestLocation2",
            notes="TestOther2",
            was_modified=False,
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
                "total_duration": 0,
                "total_size": 0,
                "robots": "",
                "was_modified": False,
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
                "total_duration": 0,
                "total_size": 0,
                "robots": "",
                "was_modified": False,
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
                "total_duration": 0,
                "total_size": 0,
                "robots": "",
                "name": "TestMission",
                "date": "2024-10-29",
                "location": "TestLocation",
                "notes": "TestOther",
                "was_modified": False,
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
                "was_modified": False,
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
                "total_duration": 0,
                "total_size": 0,
                "robots": "",
                "was_modified": False,
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
            was_modified=False,
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

    def test_get_file_invalid_path(self):
        response = self.client.get(
            reverse("get_file_by_path", kwargs={"file_path": "invalid/path"})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "No such file: invalid/path"})


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
            was_modified=False,
        )

        # Create files
        self.file1 = File.objects.create(
            id=0,
            mission=self.mission,
            file="path/to/file1",
            robot="TestRobot1",
            duration=12000,
            size=1024,
        )
        self.file2 = File.objects.create(
            id=1,
            mission=self.mission,
            file="path/to/file2",
            robot="TestRobot2",
            duration=24000,
            size=2048,
        )

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
        self.assertEqual(response.data[0]["id"], self.file1.id)
        self.assertEqual(response.data[1]["id"], self.file2.id)

    def test_get_file_by_path(self):
        response = self.client.get(
            reverse("get_file_by_path", kwargs={"file_path": self.file1.file.name})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.file1.id)
        self.assertIn(self.file1.file.name, response.data["file_path"])


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


class RestAPIDeniedTopicNamesTestCases(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        Denied_topics.objects.create(name="Car1")
        Denied_topics.objects.create(name="Car2")

    def tearDown(self):
        super().tearDown()

    def test_get_Denied_topics(self):
        response = self.client.get(
            reverse("Denied_topics"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Car1")
        self.assertEqual(response.data[1]["name"], "Car2")

    def test_create_denied_topic_name(self):
        response = self.client.post(
            reverse("Denied_topics_create"),
            {"name": "Car3"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Car3")
        self.assertTrue(Denied_topics.objects.filter(name="Car3").exists())

    def test_delete_denied_topic_name(self):
        response = self.client.delete(
            reverse("Denied_topics_delete", kwargs={"name": "Car1"}),
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Denied_topics.objects.filter(name="Car1").exists())


class RestAPITopicsByFile(APIAuthTestCase):
    def setUp(self):
        super().setUp()

        # fake storage
        self._field = File.file.field
        self._default_storage = self._field.storage
        test_storage = InMemoryStorage()
        self._field.storage = test_storage

        # create files
        file_content = ContentFile("")
        test_storage.save("path/to/file1", file_content)

        # Create a mission
        self.mission = Mission.objects.create(
            name="TestMission",
            date=timezone.now(),
            location="TestLocation",
            notes="TestOther",
            was_modified=False,
        )

        # Create file
        self.file1 = File.objects.create(
            id=0,
            mission=self.mission,
            file="path/to/file1",
            robot="TestRobot1",
            duration=12000,
            size=1024,
        )

        # Create topics
        Topic.objects.create(
            name="Car1",
            file=self.file1,
            type="sensor",
            message_count=124,
            frequency=6.5,
        )

        Topic.objects.create(
            name="Car2",
            file=self.file1,
            type="camera",
            message_count=1024,
            frequency=60,
        )

        Topic.objects.create(
            name="Car3",
            file=self.file1,
            type="imu",
            message_count=10000,
            frequency=200,
        )

    def tearDown(self):
        super().tearDown()
        self._field.storage = self._default_storage

    def test_get_topics_by_file(self):
        response = self.client.get(
            reverse("get_topics_from_files", kwargs={"file_path": "path/to/file1"}),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["name"], "Car1")
        self.assertEqual(response.data[0]["type"], "sensor")
        self.assertEqual(response.data[0]["message_count"], 124)
        self.assertEqual(response.data[0]["frequency"], 6.5)

        self.assertEqual(response.data[1]["name"], "Car2")
        self.assertEqual(response.data[1]["type"], "camera")
        self.assertEqual(response.data[1]["message_count"], 1024)
        self.assertEqual(response.data[1]["frequency"], 60)

        self.assertEqual(response.data[2]["name"], "Car3")
        self.assertEqual(response.data[2]["type"], "imu")
        self.assertEqual(response.data[2]["message_count"], 10000)
        self.assertEqual(response.data[2]["frequency"], 200)


class SetWasModifiedTestCase(APIAuthTestCase):
    def setUp(self):
        super().setUp()
        # Create a mission
        self.mission = Mission.objects.create(
            name="Test Mission",
            date="2025-01-01",
            location="Test Location",
            notes="Test Notes",
            was_modified=False,
        )

        # disable logging
        self.logger = logging.getLogger("django.request")
        self.logger.disabled = True

        # Define URLs
        self.valid_url = reverse("set_was_modified", kwargs={"pk": self.mission.id})
        self.invalid_url = reverse("set_was_modified", kwargs={"pk": 9999})
        self.valid_payload = {"was_modified": True}
        self.invalid_payload = {"wasModified": True}

    def tearDown(self):
        super().tearDown()
        # reenable logging
        self.logger.disabled = False

    def test_set_was_modified_successful(self):
        """Test setting was_modified to True for an existing mission"""
        response = self.client.put(self.valid_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.mission.id)
        self.assertTrue(response.data["was_modified"])

        # Verify the mission in the database is updated
        self.mission.refresh_from_db()
        self.assertTrue(self.mission.was_modified)

    def test_set_was_modified_mission_not_found(self):
        """Test setting was_modified for a non-existent mission"""
        response = self.client.put(self.invalid_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Mission not found")

    def test_partial_update(self):
        """Test for partial update (only 'was_modified' field is updated)"""
        new_payload = {"was_modified": True}
        old_notes = self.mission.notes
        response = self.client.put(self.valid_url, new_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mission.refresh_from_db()
        self.assertTrue(self.mission.was_modified)
        self.assertEqual(
            self.mission.notes, old_notes
        )  # make sure notes are not changed
