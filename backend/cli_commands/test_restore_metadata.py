import json
from django.test import TestCase
from cli_commands.RestoreMetadataCommand import restore_metadata
import cli_commands.RestoreMetadataCommand as RestoreMetadataCommand
from django.core.files.base import ContentFile
from restapi.models import Mission, Mission_tags
from datetime import datetime
import logging


class RestoreMetadataCommandTests(TestCase):
    def setUp(self):
        RestoreMetadataCommand.storage = RestoreMetadataCommand.DefaultStorage()
        self.test_storage = RestoreMetadataCommand.storage
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

    def test_restore_metadata(self):
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
        restore_metadata()

        # Verify mission details after restoration
        tags = Mission_tags.objects.filter(mission=self.mission)
        self.mission.refresh_from_db()
        self.assertEqual(self.mission.location, "test_location")
        self.assertEqual(self.mission.notes, "test_notes")
        self.assertEqual(tags.count(), 2)
