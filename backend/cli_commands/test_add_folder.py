import logging
from django.test import TestCase
import cli_commands.SyncCommand as SyncCommand
from restapi.models import Mission, File, Mission_files
from .AddFolderCommand import add_mission_from_folder
from django.core.files.base import ContentFile
from django.core.files.storage.memory import InMemoryStorage


class ErrorCatchingTests(TestCase):
    def test_add_mission_invalid_folder_name(self):
        with self.assertLogs(level="ERROR") as log:
            add_mission_from_folder("2024.13.02_invalid")
            self.assertFalse(Mission.objects.exists())
            self.assertIn(
                "ERROR:root:Invalid folder name format: 2024.13.02_invalid",
                log.output,
            )


class AddMissionTests(TestCase):
    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True

    def tearDown(self):
        self.logger.disabled = False

    def test_add_mission_success(self):
        add_mission_from_folder("2024.12.02_test_mission")
        self.assertTrue(
            Mission.objects.filter(name="test_mission", date="2024-12-02").exists()
        )


class AddDetailsTests(TestCase):
    def setUp(self):
        SyncCommand.storage = InMemoryStorage()
        self.test_storage = SyncCommand.storage

        # Fake files
        self.test_storage.save(
            "2024.12.02_mission1/test/bag/bag.mcap", ContentFile("123")
        )
        self.test_storage.save(
            "2024.12.02_mission1/test/bag/metadata.yaml",
            ContentFile(
                "rosbag2_bagfile_information:\n  duration:\n    nanoseconds: 14694379191"
            ),
        )

        self.logger = logging.getLogger()
        self.logger.disabled = True

    def tearDown(self):
        self.logger.disabled = False

    def test_add_mission_with_files(self):
        add_mission_from_folder("2024.12.02_mission1")
        self.assertTrue(File.objects.exists())
        self.assertTrue(Mission_files.objects.exists())
