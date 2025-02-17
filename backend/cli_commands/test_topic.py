import os
from django.test import TestCase
from restapi.models import Denied_topics, Topic, File, Mission
from django.core.files.storage.memory import InMemoryStorage
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import cli_commands.TopicCommand as TopicCommand
import logging


class TestDenyTopic(TestCase):
    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True

        denied_topic = Denied_topics.objects.create(name="test")
        denied_topic.full_clean()

        mission = Mission.objects.create(name="test", date="2025-02-17")

        self.test_storage = InMemoryStorage()
        File.file.field.storage = self.test_storage

        mcap_file = ContentFile("")
        self.test_storage.save("2024.12.02_mission1/test/bag/bag.mcap", mcap_file)

        self.file = File.objects.create(
            file="2024.12.02_mission1/test/bag/bag.mcap",
            mission=mission,
            duration=123,
            size=123,
            type="test",
        )

    def _delete_recursive(self, path: str):
        dirs, files = self.test_storage.listdir(path)
        for dir in dirs:
            self._delete_recursive(os.path.join(path, dir))
        for file in files:
            self.test_storage.delete(os.path.join(path, file))
        if path:
            self.test_storage.delete(path)

    def tearDown(self):
        self._delete_recursive("")
        self.logger.disabled = False

    def test_add_denied_topic(self):
        TopicCommand.add_denied_topic("test2")
        denied_topic = Denied_topics.objects.filter(name="test2")
        self.assertTrue(denied_topic.exists())
        self.assertEqual(len(denied_topic), 1)

    def test_add_topic_but_deny(self):
        topic = Topic.objects.create(
            file=self.file,
            name="test",
            type="example",
            message_count=123,
            frequency=123,
        )
        self.assertRaises(ValidationError, topic.full_clean)
        try:
            topic.full_clean()
        except ValidationError as e:
            self.assertIn("name", e.error_dict)


class TestAllowTopic(TestCase):
    def setUp(self):
        Denied_topics.objects.create(name="test")

    def test_allow_topic(self):
        with self.assertLogs(level="INFO") as log:
            TopicCommand.remove_denied_topic("test")
            self.assertFalse(Denied_topics.objects.filter(name="test").exists())

            self.assertIn("Removed", log.output[0])

            TopicCommand.remove_denied_topic("test")
            self.assertIn("not found", log.output[1])
