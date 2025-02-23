import json
import os
import shutil
from django.conf import settings
from django.test import TestCase
from cli_commands.RestoreDatabaseCommand import restore_database
import cli_commands.RestoreDatabaseCommand as RestoreDatabaseCommand
from django.core.files.base import ContentFile
from restapi.models import Mission, Mission_tags
from datetime import datetime
import logging
from django.core.files.storage.memory import InMemoryStorage


class RestoreDatabaseCommandTests(TestCase):
    def setUp(self):
        RestoreDatabaseCommand.storage = InMemoryStorage()
        self.test_storage = RestoreDatabaseCommand.storage
        self.test_storage.save(
            "2024.12.02_test_mission/test_mission_metadata.json", ContentFile("")
        )

        # Disable logging
        self.logger = logging.getLogger()
        self.logger.disabled = True

        # create a mission and related json file
        self.mission = Mission.objects.create(
            name="test_mission",
            date=datetime.strptime("2024.12.02", "%Y.%m.%d").date(),
        )
        self.json = {
            "location": "test_location",
            "notes": "test_notes",
            "tags": [
                {"name": "tag1", "color": "#fabfab"},
                {"name": "tag2", "color": "#027647"},
            ],
        }

    def tearDown(self):
        # Re-enable logging
        self.logger.disabled = False

        # Clean up the test files and directory
        file_path = "2024.12.02_test_mission/test_mission_metadata.json"
        if self.test_storage.exists(file_path):
            self.test_storage.delete(file_path)

        # Delete the mission directory
        dir_path = os.path.join(settings.MEDIA_ROOT, "2024.12.02_test_mission")
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

    def test_restore_database(self):
        # Verify mission details before restoration
        tags = Mission_tags.objects.filter(mission=self.mission)
        self.assertEqual(self.mission.location, None)
        self.assertEqual(self.mission.notes, None)
        self.assertEqual(tags.count(), 0)

        # Save metadata to file
        with self.test_storage.open(
            "2024.12.02_test_mission/test_mission_metadata.json", "w"
        ) as f:
            json.dump(self.json, f)

        # Call the restore function
        restore_database()

        # Verify mission details after restoration
        tags = Mission_tags.objects.filter(mission=self.mission)
        self.mission.refresh_from_db()
        self.assertEqual(self.mission.location, "test_location")
        self.assertEqual(self.mission.notes, "test_notes")
        self.assertEqual(tags.count(), 2)
