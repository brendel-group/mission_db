import logging
import os
from django.test import TestCase
from unittest.mock import patch
from restapi.models import File, Mission
from cli_commands.SyncCommand import sync_folder, sync_files
import cli_commands.SyncCommand as SyncCommand
from django.core.files.base import ContentFile
from django.core.files.storage.memory import InMemoryStorage
import io
from mcap.writer import Writer


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
        # Stop all the patchers
        self.patcher_add_mission_from_folder.stop()
        self._delete_recursive("")
        self.logger.disabled = False

    def test_sync_folder_calls_add_mission_from_folder_with_correct_arguments(self):
        """
        Test sync_folder to ensure correct arguments are passed to add_mission_from_folder.
        """
        # Call sync_folder
        sync_folder()

        # Verify add_mission_from_folder is called with correct arguments
        self.mock_add_mission_from_folder.assert_any_call(
            "2024.12.02_mission1", None, None
        )
        self.mock_add_mission_from_folder.assert_any_call(
            "2024.12.03_mission2", None, None
        )
        # Ensure add_mission_from_folder is not called for invalid folders
        self.assertEqual(self.mock_add_mission_from_folder.call_count, 2)


class SyncFilesTests(TestCase):
    def create_dummy_mcap(self):
        """Generate a small in-memory MCAP file"""
        buffer = io.BytesIO()
        writer = Writer(buffer)

        writer.start()  # Start writing the MCAP file

        # Define a dummy schema
        schema_id = writer.register_schema(
            name="ExampleSchema",
            encoding="jsonschema",
            data=b'{"type": "object", "properties": {"temperature": {"type": "number"}}}',
        )

        # Define a dummy channel
        channel_id = writer.register_channel(
            topic="/sensor/temperature",
            schema_id=schema_id,
            message_encoding="json",
        )

        # Write a dummy message
        writer.add_message(
            channel_id=channel_id,
            log_time=0,
            publish_time=0,
            data=b'{"temperature": 22.5}',
        )

        writer.add_message(
            channel_id=channel_id,
            log_time=5 * 10**9,
            publish_time=5 * 10**9,
            data=b'{"temperature": 22.5}',
        )

        writer.finish()  # Finish writing the MCAP file
        return buffer.getvalue()

    def setUp(self):
        SyncCommand.storage = InMemoryStorage()
        self.test_storage = SyncCommand.storage

        # create fake files
        mcap_file = ContentFile(self.create_dummy_mcap())
        self.test_storage.save("2024.12.02_mission1/test/bag/bag.mcap", mcap_file)

        self.mission = Mission.objects.create(
            name="mission1", date="2024-12-02", location="test_location"
        )

        self.logger = logging.getLogger()
        self.logger.disabled = True

    def tearDown(self):
        self._delete_recursive("")
        self.logger.disabled = False

    def _delete_recursive(self, path: str):
        dirs, files = self.test_storage.listdir(path)
        for dir in dirs:
            self._delete_recursive(os.path.join(path, dir))
        for file in files:
            self.test_storage.delete(os.path.join(path, file))
        if path:
            self.test_storage.delete(path)

    def test_sync_files_adds_new_files(self):
        """
        Test sync_files to ensure new files are added to the database.
        """
        sync_files("2024.12.02_mission1", self.mission)
        files = File.objects.filter(mission_id=self.mission.id)
        self.assertEqual(files.count(), 1)
        self.assertEqual(
            files.first().file,
            os.path.normpath("2024.12.02_mission1/test/bag/bag.mcap"),
        )

    def test_sync_files_removes_missing_files(self):
        """
        Test sync_files to ensure missing files are removed from the database.
        """
        # Add a file to the database that doesn't exist in the filesystem
        File.objects.create(
            file="2024.12.02_mission1/test/bag/missing.mcap",
            mission_id=self.mission.id,
            type="test",
            duration=10000000000,
            size=369629523,
        )
        sync_files("2024.12.02_mission1", self.mission)
        files = File.objects.filter(mission_id=self.mission.id)
        self.assertEqual(files.count(), 1)
        self.assertEqual(
            files.first().file,
            os.path.normpath("2024.12.02_mission1/test/bag/bag.mcap"),
        )

    def test_sync_files_handles_exceptions(self):
        """
        Test sync_files to ensure it handles exceptions gracefully.
        """
        with patch(
            "cli_commands.SyncCommand.storage.size",
            side_effect=Exception("Test exception"),
        ):
            sync_files("2024.12.02_mission1", self.mission)
            files = File.objects.filter(mission_id=self.mission.id)
            self.assertEqual(files.count(), 0)
