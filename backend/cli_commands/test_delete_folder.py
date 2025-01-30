from django.test import TestCase
from restapi.models import Mission, File
from cli_commands.DeleteFolderCommand import delete_mission_from_folder
from datetime import datetime
import logging


class DeleteFolderCommandTests(TestCase):
    def setUp(self):
        # Disable logging
        self.logger = logging.getLogger()
        self.logger.disabled = True

        # Create a mission and related files
        self.mission = Mission.objects.create(
            name="test_mission",
            date=datetime.strptime("2024.12.02", "%Y.%m.%d").date(),
        )

        self.file = File.objects.create(
            file="2024.12.02_test_mission/test_file.mcap",
            size=1024,
            duration=120.0,
            mission=self.mission,
            type="test",
        )

    def tearDown(self):
        # Re-enable logging
        self.logger.disabled = False

    def test_delete_mission_from_folder(self):
        # Verify mission and files exist before deletion
        self.assertTrue(Mission.objects.filter(name="test_mission").exists())
        self.assertTrue(
            File.objects.filter(file="2024.12.02_test_mission/test_file.mcap").exists()
        )

        # Call the delete function
        delete_mission_from_folder("2024.12.02_test_mission")

        # Verify mission and files are deleted
        self.assertFalse(Mission.objects.filter(name="test_mission").exists())
        self.assertFalse(
            File.objects.filter(file="2024.12.02_test_mission/test_file.mcap").exists()
        )

    def test_delete_nonexistent_mission(self):
        logging.getLogger().disabled = False
        with self.assertLogs(level="WARNING") as log:
            delete_mission_from_folder("2025.01.01_nonexistent_mission")

            self.assertIn(
                "WARNING:root:No mission found for name 'nonexistent_mission' and date '2025-01-01'.",
                log.output,
            )

    def test_delete_invalid_folder_name(self):
        logging.getLogger().disabled = False
        with self.assertLogs(level="WARNING") as log:
            delete_mission_from_folder("invalid_folder_name")

            self.assertIn(
                "ERROR:root:Folder name 'invalid_folder_name' does not match the expected format (YYYY.MM.DD_missionname).",
                log.output,
            )
