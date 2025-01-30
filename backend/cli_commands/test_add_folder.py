import os
from django.test import TestCase
from restapi.models import Mission, File
from cli_commands.AddFolderCommand import (
    add_mission_from_folder,
    extract_info_from_folder,
)
import cli_commands.AddFolderCommand as AddFolderCommand
from datetime import datetime
import logging
from django.core.files.base import ContentFile
from django.core.files.storage.memory import InMemoryStorage


class ErrorCatchingTests(TestCase):
    def test_add_mission_from_folder(self):
        with self.assertLogs(level="WARNING") as log:
            add_mission_from_folder("2024.13.02_test_add_mission")
            self.assertFalse(
                Mission.objects.filter(
                    name="test_add_mission", date="2024-12-02"
                ).exists()
            )
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:Folder name '2024.13.02_test_add_mission' does not match the expected format (YYYY.MM.DD_missionname).",
                    "WARNING:root:Skipping folder due to naming issues.",
                ],
            )

    def test_extract_info_from_folder(self):
        with self.assertLogs(level="WARNING") as log:
            mission_date, name = extract_info_from_folder("2024.13.30_test")
            self.assertIsNone(mission_date)
            self.assertIsNone(name)
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:Folder name '2024.13.30_test' does not match the expected format (YYYY.MM.DD_missionname)."
                ],
            )


class AddMissionTests(TestCase):
    def setUp(self):
        # disable logging
        self.logger = logging.getLogger()
        self.logger.disabled = True

    def tearDown(self):
        # reenable logging
        self.logger.disabled = False

    def test_add_mission_from_folder(self):
        add_mission_from_folder("2024.12.02_test_add_mission")
        self.assertTrue(
            Mission.objects.filter(name="test_add_mission", date="2024-12-02").exists()
        )
        add_mission_from_folder(
            "2024.12.02_test_add_mission_2", "TestLocation", "other info"
        )
        self.assertTrue(
            Mission.objects.filter(
                name="test_add_mission_2",
                date="2024-12-02",
                location="TestLocation",
                notes="other info",
            ).exists()
        )


class AddDetailsTests(TestCase):
    def setUp(self):
        AddFolderCommand.storage = InMemoryStorage()
        self.test_storage = AddFolderCommand.storage

        # create fake files
        mcap_file = ContentFile("123")
        yaml_file = ContentFile(
            "rosbag2_bagfile_information:\n  duration:\n    nanoseconds: 14694379191"
        )
        self.test_storage.save("2024.12.02_mission1/test/bag/bag.mcap", mcap_file)
        self.test_storage.save("2024.12.02_mission1/test/bag/metadata.yaml", yaml_file)

        # disable logging
        self.logger = logging.getLogger()
        self.logger.disabled = True

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

        # reenable logging
        self.logger.disabled = False

    def test_add_details(self):
        add_mission_from_folder("2024.12.02_mission1")
        file = File.objects.filter(file="2024.12.02_mission1/test/bag/bag.mcap")
        self.assertTrue(file.exists())
        self.assertEqual(len(file), 1)
        self.assertEqual(file.first().size, 3)
        self.assertEqual(file.first().duration, 14)
        self.assertEqual(file.first().type, "test")


class BasicTests(TestCase):
    def test_extract_info_from_folder(self):
        mission_date, name = extract_info_from_folder("2024.11.30_test")
        self.assertEqual(
            mission_date, datetime.strptime("2024.11.30", "%Y.%m.%d").date()
        )
        self.assertEqual(name, "test")
