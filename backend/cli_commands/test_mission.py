from django.test import TestCase
from datetime import date, datetime
from cli_commands.MissionCommand import (
    validate_date,
    add_mission,
    remove_mission,
    list_tags_by_mission,
    add_tag_to_mission,
    remove_tag_from_mission,
)
from restapi.models import Mission, Tag, Mission_tags
from io import StringIO
import logging
import sys
import os
from unittest.mock import patch


class BasicTests(TestCase):
    def test_validate_date(self):
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        self.assertEqual(validate_date(date_str), today)
        self.assertEqual(
            validate_date("2024-12-02"),
            datetime.strptime("2024-12-02", "%Y-%m-%d").date(),
        )


class ErrorCatchingTests(TestCase):
    def test_validate_date(self):
        with self.assertLogs(level="WARNING") as log:
            self.assertIsNone(validate_date("Wrong format"))
            self.assertIsNone(validate_date("2024-13-02"))
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:Date and time format should be YYYY-MM-DD.",
                    "ERROR:root:Date and time format should be YYYY-MM-DD.",
                ],
            )

    def test_add_mission_invalid_date(self):
        with self.assertLogs(level="WARNING") as log:
            add_mission("TestInvalidDate", "2024-13-02")
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:Error adding mission: {'date': ['“2024-13-02” value has the correct format (YYYY-MM-DD) but it is an invalid date.']}"
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

    def test_add_mission(self):
        add_mission("TestAddMission", "2024-12-02")
        self.assertTrue(
            Mission.objects.filter(name="TestAddMission", date="2024-12-02").exists()
        )
        add_mission("TestAddMission", "2024-12-02")
        self.assertEqual(
            len(Mission.objects.filter(name="TestAddMission", date="2024-12-02")), 1
        )
        add_mission("TestAddMission2", "2024-12-02", notes="notes")
        self.assertTrue(
            Mission.objects.filter(
                name="TestAddMission2", date="2024-12-02", notes="notes"
            ).exists()
        )


class CapturedOutputTest(TestCase):
    def setUp(self):
        self.mission = Mission.objects.create(name="TestRemove", date=date.today())
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        self.mission.delete()
        sys.stdout = self.original_stdout

    def test_remove_misison(self):
        remove_mission(self.mission.id)
        sys.stdout.flush()
        self.assertFalse(Mission.objects.filter(id=self.mission.id).exists())
        self.assertEqual(
            self.captured_output.getvalue().strip(),
            f"Mission with ID {self.mission.id} has been removed.",
        )

    def test_remove_mission_failed(self):
        id_no_mission = 1
        while Mission.objects.filter(id=id_no_mission).exists():
            id_no_mission += 1
        remove_mission(id_no_mission)
        sys.stdout.flush()
        self.assertTrue(Mission.objects.filter(id=self.mission.id).exists())
        self.assertEqual(
            self.captured_output.getvalue().strip(),
            f"No mission found with ID {id_no_mission}.",
        )


class ListMissionTagTests(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

        self.patcher_os_terminal_size = patch(
            "os.get_terminal_size",
            return_value=os.terminal_size((float("inf"), float("inf"))),
        )
        self.patcher_os_terminal_size.start()

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

        self.patcher_os_terminal_size.stop()

    def test_list_tags_by_mission(self):
        list_tags_by_mission(self.mission.id)
        sys.stdout.flush()
        self.assertIn(self.tag1.name, self.captured_output.getvalue())
        self.assertIn(self.tag2.name, self.captured_output.getvalue())

    def test_list_tag_by_mission_not_existent(self):
        list_tags_by_mission(self.mission.id + 1)
        sys.stdout.flush()
        self.assertEqual(
            "Empty list nothing to display", self.captured_output.getvalue().strip()
        )


class AddTagToMissionTests(TestCase):
    def setUp(self):
        self.mission = Mission(name="TestMission", date=date.today())
        self.mission.save()

        self.tag = Tag(name="TestTag")
        self.tag.save()

    def test_add_tag_to_mission(self):
        self.assertFalse(
            Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
        )
        with self.assertLogs(level="INFO") as log:
            add_tag_to_mission(self.mission.id, self.tag.id)
            self.assertEqual(
                log.output,
                [
                    f"INFO:root:Tagged Mission with id {self.mission.id} with '{self.tag.name}'"
                ],
            )
            self.assertTrue(
                Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
            )

        # Add the same tag again for error
        with self.assertLogs(level="INFO") as log:
            add_tag_to_mission(self.mission.id, self.tag.id)
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:{'__all__': ['Mission_tags with this Mission and Tag already exists.']}"
                ],
            )
            mission_tags = Mission_tags.objects.filter(
                mission=self.mission, tag=self.tag
            )
            self.assertTrue(mission_tags.exists())
            self.assertEqual(len(mission_tags), 1)

    def test_add_tag_to_mission_create(self):
        with self.assertLogs(level="INFO") as log:
            self.assertFalse(
                Mission_tags.objects.filter(
                    mission=self.mission, tag__name="NewTag"
                ).exists()
            )
            add_tag_to_mission(self.mission.id, tag_name="NewTag")
            self.assertEqual(
                log.output,
                [
                    f"INFO:root:Tag 'NewTag' created and tagged Mission with id {self.mission.id}"
                ],
            )
            self.assertTrue(
                Mission_tags.objects.filter(
                    mission=self.mission, tag__name="NewTag"
                ).exists()
            )


class RemoveTagFromMissionTests(TestCase):
    def setUp(self):
        self.mission = Mission(name="TestMission", date=date.today())
        self.mission.save()

        self.tag = Tag(name="TestTag")
        self.tag.save()

        self.mission_tag = Mission_tags(mission=self.mission, tag=self.tag)
        self.mission_tag.save()

    def test_remove_tag_from_mission(self):
        self.assertTrue(
            Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
        )
        with self.assertLogs(level="INFO") as log:
            remove_tag_from_mission(self.mission.id, self.tag.id)
            self.assertEqual(
                log.output,
                [
                    f"INFO:root:Removed Tag '{self.tag.name}' from Mission with id {self.mission.id}"
                ],
            )
            self.assertFalse(
                Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
            )

        # remove same tag again for error
        with self.assertLogs(level="INFO") as log:
            remove_tag_from_mission(self.mission.id, self.tag.id)
            self.assertEqual(
                log.output,
                [
                    f"ERROR:root:No Tag with id {self.tag.id} found at Mission with id {self.mission.id}"
                ],
            )
            self.assertFalse(
                Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
            )

    def test_remove_tag_from_mission_by_name(self):
        with self.assertLogs(level="INFO") as log:
            remove_tag_from_mission(self.mission.id, tag_name=self.tag.name)
            self.assertEqual(
                log.output,
                [
                    f"INFO:root:Removed Tag '{self.tag.name}' from Mission with id {self.mission.id}"
                ],
            )
            self.assertFalse(
                Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
            )
