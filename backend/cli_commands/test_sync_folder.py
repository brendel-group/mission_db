from django.test import TestCase
from unittest.mock import patch
from cli_commands.SyncFolderCommand import sync_folder


class SyncFolderArgumentTests(TestCase):
    def setUp(self):
        # Start the patchers
        self.patcher_join = patch(
            "os.path.join", side_effect=lambda *args: "/".join(args)
        )
        self.patcher_listdir = patch("os.listdir")
        self.patcher_isdir = patch("os.path.isdir")
        self.patcher_add_mission_from_folder = patch(
            "cli_commands.SyncFolderCommand.add_mission_from_folder"
        )

        # Start patching
        self.mock_join = self.patcher_join.start()
        self.mock_listdir = self.patcher_listdir.start()
        self.mock_isdir = self.patcher_isdir.start()
        self.mock_add_mission_from_folder = self.patcher_add_mission_from_folder.start()

        # Define the default mock behavior
        self.mock_listdir.return_value = [
            "2024.12.02_mission1",
            "2024.12.03_mission2",
            "invalid_folder",
        ]
        self.mock_isdir.side_effect = lambda path: path in [
            "/test",
            "/test/2024.12.02_mission1",
            "/test/2024.12.03_mission2",
        ]

    def tearDown(self):
        # Stop all the patchers
        self.patcher_join.stop()
        self.patcher_listdir.stop()
        self.patcher_isdir.stop()
        self.patcher_add_mission_from_folder.stop()

    def test_sync_folder_calls_add_mission_from_folder_with_correct_arguments(self):
        """
        Test sync_folder to ensure correct arguments are passed to add_mission_from_folder.
        """
        # Call sync_folder
        sync_folder("/test")

        # Verify add_mission_from_folder is called with correct arguments
        self.mock_add_mission_from_folder.assert_any_call(
            "/test/2024.12.02_mission1", None, None
        )
        self.mock_add_mission_from_folder.assert_any_call(
            "/test/2024.12.03_mission2", None, None
        )
        # Ensure add_mission_from_folder is not called for invalid folders
        self.assertEqual(self.mock_add_mission_from_folder.call_count, 2)
