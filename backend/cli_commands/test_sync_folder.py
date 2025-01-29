import os
from django.test import TestCase
from unittest.mock import patch
from cli_commands.SyncCommand import sync_folder
import cli_commands.SyncCommand as SyncCommand
from django.core.files.base import ContentFile
from django.core.files.storage.memory import InMemoryStorage


class SyncFolderArgumentTests(TestCase):
    def setUp(self):
        SyncCommand.storage = InMemoryStorage()
        self.test_storage = SyncCommand.storage

        # create fake files
        empty_file = ContentFile("")
        yaml_file = ContentFile(
            "rosbag2_bagfile_information:\n  duration:\n    nanoseconds: 14694379191"
        )
        self.test_storage.save("2024.12.02_mission1/test/bag/bag.mcap", empty_file)
        self.test_storage.save("2024.12.02_mission1/test/bag/metadata.yaml", yaml_file)
        self.test_storage.save("2024.12.03_mission2/test/bag/bag.mcap", empty_file)
        self.test_storage.save("2024.12.03_mission2/test/bag/metadata.yaml", yaml_file)
        self.test_storage.save("some_file", empty_file)

        # Start the patchers
        self.patcher_add_mission_from_folder = patch(
            "cli_commands.SyncCommand.add_mission_from_folder"
        )

        # Start patching
        self.mock_add_mission_from_folder = self.patcher_add_mission_from_folder.start()

    def _delete_recursive(self, path: str):
        dirs, files = self.test_storage.listdir(path)
        for dir in dirs:
            self._delete_recursive(os.path.join(path, dir))
        for file in files:
            self.test_storage.delete(os.path.join(path, file))
        if path:
            self.test_storage.delete(path)

    def tearDown(self):
        # Stop all the patchers
        self.patcher_add_mission_from_folder.stop()
        self._delete_recursive("")

    def test_sync_folder_calls_add_mission_from_folder_with_correct_arguments(self):
        """
        Test sync_folder to ensure correct arguments are passed to add_mission_from_folder.
        """
        # Call sync_folder
        sync_folder()

        # Verify add_mission_from_folder is called with correct arguments
        self.mock_add_mission_from_folder.assert_any_call(
            "2024.12.02_mission1"
        )
        self.mock_add_mission_from_folder.assert_any_call(
            "2024.12.03_mission2"
        )
        # Ensure add_mission_from_folder is not called for invalid folders
        self.assertEqual(self.mock_add_mission_from_folder.call_count, 2)
