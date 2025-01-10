import logging
import sys
import os
from io import StringIO
from django.test import TestCase
from cli_commands.TagCommand import (
    add_tag,
    remove_tag,
    change_tag,
    list_tags,
    list_missions_by_tag,
)
from restapi.models import Tag, Mission, Mission_tags
from datetime import date
from unittest.mock import patch


class TagFunctionLogTests(TestCase):
    def test_add_tag_error_on_duplicate(self):
        Tag.objects.create(name="UniqueTag", color="#123456")
        with self.assertLogs(level="ERROR") as log:
            # Adding a tag with the same name should trigger a validation error
            add_tag("UniqueTag", "#654321")
            self.assertIn("ERROR:root:Error adding Tag:", log.output[0])

    def test_remove_tag_not_found_logging(self):
        with self.assertLogs(level="ERROR") as log:
            remove_tag(name="NonExistentTag")
            self.assertEqual(
                log.output, ["ERROR:root:No Tag found with name 'NonExistentTag'."]
            )

    def test_change_tag_no_change_logging(self):
        tag = Tag.objects.create(name="NoChange", color="#333333")
        with self.assertLogs(level="INFO") as log:
            change_tag(id=tag.id)  # No change provided
            self.assertEqual(log.output, ["INFO:root:Nothing to change"])


class BasicTests(TestCase):
    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True

        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

        self.patcher_os_terminal_size = patch(
            "os.get_terminal_size",
            return_value=os.terminal_size((float("inf"), float("inf"))),
        )
        self.patcher_os_terminal_size.start()

        # Setting up environment, creating common tags
        self.tag = Tag.objects.create(name="TestTag", color="#FFFFFF")

    def tearDown(self):
        self.logger.disabled = False

        self.patcher_os_terminal_size.stop()

        sys.stdout.flush()
        sys.stdout = self.original_stdout
        Tag.objects.all().delete()  # Clean up after tests

    def test_add_tag(self):
        add_tag("NewTagCLI", "#123123")
        self.assertTrue(Tag.objects.filter(name="NewTagCLI", color="#123123").exists())

    def test_remove_tag_by_name(self):
        remove_tag(name="TestTag")
        self.assertFalse(Tag.objects.filter(name="TestTag").exists())

    def test_remove_tag_by_id(self):
        remove_tag(id=self.tag.id)
        self.assertFalse(Tag.objects.filter(id=self.tag.id).exists())

    def test_list_tags(self):
        list_tags()
        sys.stdout.flush()
        self.assertIn("TestTag", self.captured_output.getvalue())

    def test_change_tag_command(self):
        change_tag(id=self.tag.id, name="UpdatedTag", color="#000000")
        updated_tag = Tag.objects.get(id=self.tag.id)
        self.assertEqual(updated_tag.name, "UpdatedTag")
        self.assertEqual(updated_tag.color, "#000000")


class ListMissionTagTests(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

        self.mission = Mission(name="Test", date=date.today())
        self.mission.save()

        self.tag1 = Tag(name="TestTag1")
        self.tag1.save()
        self.tag2 = Tag(name="TestTag2")
        self.tag2.save()

        self.mission_tag1 = Mission_tags(mission=self.mission, tag=self.tag1)
        self.mission_tag1.save()
        self.mission_tag2 = Mission_tags(mission=self.mission, tag=self.tag2)
        self.mission_tag2.save()

    def tearDown(self):
        sys.stdout.flush()
        sys.stdout = self.original_stdout

    def test_list_mission_by_tag_id(self):
        list_missions_by_tag(self.tag1.id)
        sys.stdout.flush()
        self.assertIn(self.mission.name, self.captured_output.getvalue())

    def test_list_mission_by_tag_name(self):
        list_missions_by_tag(name=self.tag1.name)
        sys.stdout.flush()
        self.assertIn(self.mission.name, self.captured_output.getvalue())

    def test_list_mission_by_tag_empty(self):
        list_missions_by_tag(name="NonexistentTag")
        sys.stdout.flush()
        self.assertEqual(
            "Empty list nothing to display", self.captured_output.getvalue().strip()
        )


class ListMissionTagLogTests(TestCase):
    def setUp(self):
        self.tag1 = Tag(name="Test")
        self.tag1.save()

    def test_list_mission_by_tag_no_args(self):
        with self.assertLogs(level="ERROR") as log:
            list_missions_by_tag()
            self.assertEqual(
                log.output,
                ["ERROR:root:At least one of --id or --name must be provided"],
            )

    def test_list_mission_by_tag_mismatch_id_name(self):
        with self.assertLogs(level="ERROR") as log:
            list_missions_by_tag(self.tag1.id, "WrongName")
            self.assertEqual(
                log.output, ["ERROR:root:Tag id and name given but dont match."]
            )

    def test_list_mission_by_tag_wrong_id(self):
        with self.assertLogs(level="ERROR") as log:
            list_missions_by_tag(self.tag1.id + 10, self.tag1.name)
            self.assertEqual(
                log.output, [f"ERROR:root:No Tag with id {self.tag1.id+10} found"]
            )
