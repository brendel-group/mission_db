from django.test import TestCase
from datetime import date, datetime
from restapi.models import Mission, Tag, Mission_tags
from restapi.serializer import MissionSerializer, TagSerializer
import cli
import logging
from io import StringIO
import sys
from unittest.mock import patch
from rest_framework_api_key.models import APIKey
from django.contrib.auth.models import User


class SyncFolderArgumentTests(TestCase):
    def setUp(self):
        # Start the patchers
        self.patcher_join = patch(
            "os.path.join", side_effect=lambda *args: "/".join(args)
        )
        self.patcher_listdir = patch("os.listdir")
        self.patcher_isdir = patch("os.path.isdir")
        self.patcher_add_mission_from_folder = patch("cli.add_mission_from_folder")

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
        cli.sync_folder("/test")

        # Verify add_mission_from_folder is called with correct arguments
        self.mock_add_mission_from_folder.assert_any_call(
            "/test/2024.12.02_mission1", None, None
        )
        self.mock_add_mission_from_folder.assert_any_call(
            "/test/2024.12.03_mission2", None, None
        )
        # Ensure add_mission_from_folder is not called for invalid folders
        self.assertEqual(self.mock_add_mission_from_folder.call_count, 2)


class BasicCLITests(TestCase):
    def setUp(self):
        self.mission = Mission(name="Test", date=date.today())
        self.mission.save()

    def test_extract_info_from_folder(self):
        mission_date, name = cli.extract_info_from_folder("2024.11.30_test")
        self.assertEqual(
            mission_date, datetime.strptime("2024.11.30", "%Y.%m.%d").date()
        )
        self.assertEqual(name, "test")

    def test_check_mission_exists(self):
        id = self.mission.id
        self.assertTrue(cli.check_mission_exists(id))
        self.assertFalse(cli.check_mission_exists(id + 1))

    def test_validate_date(self):
        today = date.today()
        date_str = today.strftime("%Y-%m-%d")
        self.assertEqual(cli.validate_date(date_str), today)
        self.assertEqual(
            cli.validate_date("2024-12-02"),
            datetime.strptime("2024-12-02", "%Y-%m-%d").date(),
        )


class ErrorCatchingTests(TestCase):
    def test_validate_date(self):
        with self.assertLogs(level="WARNING") as log:
            self.assertIsNone(cli.validate_date("Wrong format"))
            self.assertIsNone(cli.validate_date("2024-13-02"))
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:Date and time format should be YYYY-MM-DD.",
                    "ERROR:root:Date and time format should be YYYY-MM-DD.",
                ],
            )

    def test_extract_info_from_folder(self):
        with self.assertLogs(level="WARNING") as log:
            mission_date, name = cli.extract_info_from_folder("2024.13.30_test")
            self.assertIsNone(mission_date)
            self.assertIsNone(name)
            self.assertEqual(
                log.output,
                [
                    "ERROR:root:Folder name '2024.13.30_test' does not match the expected format (YYYY.MM.DD_missionname)."
                ],
            )

    def test_add_mission_from_folder(self):
        with self.assertLogs(level="WARNING") as log:
            cli.add_mission_from_folder("2024.13.02_test_add_mission")
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

    def test_add_mission_invalid_date(self):
        with self.assertLogs(level="WARNING") as log:
            cli.add_mission("TestInvalidDate", "2024-13-02")
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

    def test_add_mission_from_folder(self):
        cli.add_mission_from_folder("2024.12.02_test_add_mission")
        self.assertTrue(
            Mission.objects.filter(name="test_add_mission", date="2024-12-02").exists()
        )
        cli.add_mission_from_folder(
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

    def test_add_mission(self):
        cli.add_mission("TestAddMission", "2024-12-02")
        self.assertTrue(
            Mission.objects.filter(name="TestAddMission", date="2024-12-02").exists()
        )
        cli.add_mission("TestAddMission", "2024-12-02")
        self.assertEqual(
            len(Mission.objects.filter(name="TestAddMission", date="2024-12-02")), 1
        )
        cli.add_mission("TestAddMission2", "2024-12-02", notes="notes")
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
        cli.remove_mission(self.mission.id)
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
        cli.remove_mission(id_no_mission)
        sys.stdout.flush()
        self.assertTrue(Mission.objects.filter(id=self.mission.id).exists())
        self.assertEqual(
            self.captured_output.getvalue().strip(),
            f"No mission found with ID {id_no_mission}.",
        )


class MainFunctionTests(TestCase):
    def setUp(self):
        self.mission = Mission.objects.create(name="TestRemove", date=date.today())
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        self.mission.delete()
        sys.stdout.flush()
        sys.stdout = self.original_stdout

    def test_mission_add(self):
        args = [
            "mission",
            "add",
            "--name",
            "Test",
            "--date",
            "2024-12-02",
        ]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            self.assertTrue(
                Mission.objects.filter(name="Test", date="2024-12-02").exists()
            )
            self.assertEqual(log.output, ["INFO:root:'Test' added."])

    def test_mission_add_all(self):
        args = [
            "mission",
            "add",
            "--name",
            "Test",
            "--date",
            "2024-12-02",
            "--location",
            "Tübingen",
            "--notes",
            "Test with all fields",
        ]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            self.assertTrue(
                Mission.objects.filter(
                    name="Test",
                    date="2024-12-02",
                    location="Tübingen",
                    notes="Test with all fields",
                ).exists()
            )
            self.assertEqual(log.output, ["INFO:root:'Test' added."])

    def test_mission_remove(self):
        args = ["mission", "remove", "--id", str(self.mission.id)]
        cli.main(args)
        sys.stdout.flush()
        self.assertFalse(Mission.objects.filter(id=self.mission.id).exists())

        self.assertEqual(
            self.captured_output.getvalue().strip(),
            f"Mission with ID {self.mission.id} has been removed.",
        )

        # Try to delete the same mission again

        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        cli.main(args)
        sys.stdout.flush()
        self.assertEqual(
            self.captured_output.getvalue().strip(),
            f"No mission found with ID {self.mission.id}.",
        )

    def test_mission_list(self):
        missions = Mission.objects.all()
        serializer = MissionSerializer(missions, many=True)
        cli.print_table(serializer.data)
        sys.stdout.flush()
        table = self.captured_output.getvalue().strip()
        args = ["mission", "list"]
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        cli.main(args)

        # Compare output of main with output of print_table(missions)
        self.assertEqual(self.captured_output.getvalue().strip(), table)

    def test_addfolder(self):
        args = ["addfolder", "--path", "2024.12.02_test"]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            self.assertTrue(
                Mission.objects.filter(name="test", date="2024-12-02").exists()
            )
            self.assertEqual(
                log.output,
                ["INFO:root:Mission 'test' from folder '2024.12.02_test' added."],
            )

    def test_add_tag_command(self):
        args = ["tag", "add", "--name", "CLI_Tag", "--color", "#123123"]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            self.assertTrue(
                Tag.objects.filter(name="CLI_Tag", color="#123123").exists()
            )
            self.assertEqual(log.output, ["INFO:root:'CLI_Tag' Tag added."])

    def test_remove_tag_command(self):
        tag = Tag.objects.create(name="RemoveMe", color="#ABCDEF")
        args = ["tag", "remove", "--id", str(tag.id)]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            self.assertFalse(Tag.objects.filter(id=tag.id).exists())
            self.assertEqual(log.output, ["INFO:root:Tag 'RemoveMe' has been removed."])

    def test_list_tags_command(self):
        Tag.objects.create(name="ListTag1", color="#CCCCCC")
        Tag.objects.create(name="ListTag2", color="#333333")
        args = ["tag", "list"]
        cli.main(args)
        sys.stdout.flush()
        self.assertIn("ListTag1", self.captured_output.getvalue())
        self.assertIn("ListTag2", self.captured_output.getvalue())

    def test_change_tag_command(self):
        tag = Tag.objects.create(name="ChangeThis", color="#AAAAAA")
        args = [
            "tag",
            "change",
            "--id",
            str(tag.id),
            "--name",
            "Changed",
            "--color",
            "#FFFFFF",
        ]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            updated_tag = Tag.objects.get(id=tag.id)
            self.assertEqual(updated_tag.name, "Changed")
            self.assertEqual(updated_tag.color, "#FFFFFF")
            self.assertEqual(log.output, [f"INFO:root:Tag changed to '{updated_tag}'"])


class TagFunctionLogTests(TestCase):
    def test_add_tag_error_on_duplicate(self):
        Tag.objects.create(name="UniqueTag", color="#123456")
        with self.assertLogs(level="ERROR") as log:
            # Adding a tag with the same name should trigger a validation error
            cli.add_tag("UniqueTag", "#654321")
            self.assertIn("ERROR:root:Error adding Tag:", log.output[0])

    def test_remove_tag_not_found_logging(self):
        with self.assertLogs(level="ERROR") as log:
            cli.remove_tag(name="NonExistentTag")
            self.assertEqual(
                log.output, ["ERROR:root:No Tag found with name 'NonExistentTag'."]
            )

    def test_change_tag_no_change_logging(self):
        tag = Tag.objects.create(name="NoChange", color="#333333")
        with self.assertLogs(level="INFO") as log:
            cli.change_tag(id=tag.id)  # No change provided
            self.assertEqual(log.output, ["INFO:root:Nothing to change"])


class TagBasicTests(TestCase):
    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.disabled = True

        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

        # Setting up environment, creating common tags
        self.tag = Tag.objects.create(name="TestTag", color="#FFFFFF")

    def tearDown(self):
        self.logger.disabled = False

        sys.stdout.flush()
        sys.stdout = self.original_stdout
        Tag.objects.all().delete()  # Clean up after tests

    def test_add_tag(self):
        cli.add_tag("NewTagCLI", "#123123")
        self.assertTrue(Tag.objects.filter(name="NewTagCLI", color="#123123").exists())

    def test_remove_tag_by_name(self):
        cli.remove_tag(name="TestTag")
        self.assertFalse(Tag.objects.filter(name="TestTag").exists())

    def test_remove_tag_by_id(self):
        cli.remove_tag(id=self.tag.id)
        self.assertFalse(Tag.objects.filter(id=self.tag.id).exists())

    def test_list_tags(self):
        cli.list_tags()
        sys.stdout.flush()
        self.assertIn("TestTag", self.captured_output.getvalue())

    def test_change_tag_command(self):
        cli.change_tag(id=self.tag.id, name="UpdatedTag", color="#000000")
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

    def test_list_tags_by_mission(self):
        cli.list_tags_by_mission(self.mission.id)
        sys.stdout.flush()
        self.assertIn(self.tag1.name, self.captured_output.getvalue())
        self.assertIn(self.tag2.name, self.captured_output.getvalue())

    def test_list_mission_by_tag_id(self):
        cli.list_missions_by_tag(self.tag1.id)
        sys.stdout.flush()
        self.assertIn(self.mission.name, self.captured_output.getvalue())

    def test_list_mission_by_tag_name(self):
        cli.list_missions_by_tag(name=self.tag1.name)
        sys.stdout.flush()
        self.assertIn(self.mission.name, self.captured_output.getvalue())

    def test_list_tag_by_mission_not_existent(self):
        cli.list_tags_by_mission(self.mission.id + 1)
        sys.stdout.flush()
        self.assertEqual(
            "Empty list nothing to display", self.captured_output.getvalue().strip()
        )

    def test_list_mission_by_tag_empty(self):
        cli.list_missions_by_tag(name="NonexistentTag")
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
            cli.list_missions_by_tag()
            self.assertEqual(
                log.output,
                ["ERROR:root:At least one of --id or --name must be provided"],
            )

    def test_list_mission_by_tag_mismatch_id_name(self):
        with self.assertLogs(level="ERROR") as log:
            cli.list_missions_by_tag(self.tag1.id, "WrongName")
            self.assertEqual(
                log.output, ["ERROR:root:Tag id and name given but dont match."]
            )

    def test_list_mission_by_tag_wrong_id(self):
        with self.assertLogs(level="ERROR") as log:
            cli.list_missions_by_tag(self.tag1.id + 10, self.tag1.name)
            self.assertEqual(
                log.output, [f"ERROR:root:No Tag with id {self.tag1.id+10} found"]
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
            cli.add_tag_to_mission(self.mission.id, self.tag.id)
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
            cli.add_tag_to_mission(self.mission.id, self.tag.id)
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
            cli.add_tag_to_mission(self.mission.id, tag_name="NewTag")
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
            cli.remove_tag_from_mission(self.mission.id, self.tag.id)
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
            cli.remove_tag_from_mission(self.mission.id, self.tag.id)
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
            cli.remove_tag_from_mission(self.mission.id, tag_name=self.tag.name)
            self.assertEqual(
                log.output,
                [
                    f"INFO:root:Removed Tag '{self.tag.name}' from Mission with id {self.mission.id}"
                ],
            )
            self.assertFalse(
                Mission_tags.objects.filter(mission=self.mission, tag=self.tag).exists()
            )


class APIKeyTests(TestCase):
    def setUp(self):
        APIKey.objects.create_key(name="Test")
        self.key = APIKey.objects.get(name="Test")

    def test_add_key(self):
        with self.assertLogs(level="INFO") as log:
            cli.add_api_key(name="Test2")
            self.assertTrue(APIKey.objects.filter(name="Test2").exists())
            self.assertIn("Test2", log.output[0])
            self.assertIn("key: ", log.output[0])

    def test_remove_key(self):
        with self.assertLogs(level="INFO") as log:
            cli.remove_api_key(name=self.key.name)
            self.assertFalse(APIKey.objects.filter(name=self.key.name).exists())
            self.assertIn(self.key.name, log.output[0])
            self.assertIn("Removed", log.output[0])


class PrintTableTests(TestCase):
    def setUp(self):
        self.mission = Mission.objects.create(name="TestRemove", date=date.today())
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output
        cli.USE_UNICODE = True

    def tearDown(self):
        self.mission.delete()
        sys.stdout = self.original_stdout

    def test_print_mission_table(self):
        missions = [
            Mission.objects.create(name=f"Test{i}", date="2024-12-02") for i in range(3)
        ]
        serializer = MissionSerializer(missions, many=True)
        cli.print_table(serializer.data)
        sys.stdout.flush()
        self.assertEqual(
            self.captured_output.getvalue().strip().replace(" ", "").replace("─", ""),
            "id│name│date│location│notes\n"
            + "┼┼┼┼\n"
            + f"{missions[0].id}│Test0│2024-12-02│None│None\n"
            + f"{missions[1].id}│Test1│2024-12-02│None│None\n"
            + f"{missions[2].id}│Test2│2024-12-02│None│None",
        )

    def test_print_tag_table(self):
        tags = [Tag.objects.create(name=f"Test{i}") for i in range(3)]
        serializer = TagSerializer(tags, many=True)
        cli.print_table(serializer.data)
        sys.stdout.flush()
        self.assertEqual(
            self.captured_output.getvalue().strip().replace(" ", "").replace("─", ""),
            "id│name│color\n"
            + "┼┼\n"
            + f"{tags[0].id}│{tags[0].name}│#FFFFFF\n"
            + f"{tags[1].id}│{tags[1].name}│#FFFFFF\n"
            + f"{tags[2].id}│{tags[2].name}│#FFFFFF",
        )

    def test_mission_with_newline(self):
        mission = [
            Mission.objects.create(
                name="Test\nlinebreak", date="2024-12-26", notes="Test\nwith\nnewline"
            )
        ]
        serializer = MissionSerializer(mission, many=True)
        cli.print_table(serializer.data)
        sys.stdout.flush()
        self.assertEqual(
            self.captured_output.getvalue().strip().replace(" ", "").replace("─", ""),
            "id│name│date│location│notes\n"
            + "┼┼┼┼\n"
            + f"{mission[0].id}│Test│2024-12-26│None│Test\n"
            + "│linebreak│││with\n"
            + "││││newline",
        )


class PasswordInputTests(TestCase):
    def setUp(self):
        super().setUp()
        self.patcher_getpass = patch("cli.getpass", return_value="test12345!")
        self.patcher_validate = patch("cli.validate_password")
        self.patcher_check = patch("cli.User.check_password", return_value=False)

        self.mock_getpass = self.patcher_getpass.start()
        self.mock_validate = self.patcher_validate.start()
        self.mock_check = self.patcher_check.start()

    def tearDown(self):
        super().tearDown()
        self.patcher_getpass.stop()
        self.patcher_validate.stop()
        self.patcher_check.stop()

    def test_add_user(self):
        with self.assertLogs(level="INFO") as log:
            cli.add_user("test_user")
            self.assertTrue(User.objects.filter(username="test_user").exists())
            self.assertIn("User 'test_user' added", log.output[0])
            self.assertEqual(self.mock_getpass.call_count, 2)
            self.assertEqual(self.mock_validate.call_count, 1)
            self.assertEqual(self.mock_check.call_count, 0)

    def test_remove_user(self):
        with self.assertLogs(level="INFO") as log:
            User.objects.create_user(username="test", password="test")
            cli.remove_user("test")
            self.assertFalse(User.objects.filter(username="test").exists())
            self.assertIn("User 'test' removed", log.output[0])

    def test_change_password(self):
        with self.assertLogs(level="INFO") as log:
            User.objects.create_user(username="test_change", password="test")
            cli.change_password("test_change")
            self.assertIn("changed successfully", log.output[0])
            self.assertEqual(self.mock_getpass.call_count, 2)
            self.assertEqual(self.mock_validate.call_count, 1)
            self.assertEqual(self.mock_check.call_count, 1)

            self.patcher_check.stop()

            # changing again to same password should not work
            cli.change_password("test_change")
            self.assertIn("same as the old password", log.output[1])
            self.assertEqual(self.mock_getpass.call_count, 4)
            self.assertEqual(self.mock_validate.call_count, 2)
            self.assertEqual(self.mock_check.call_count, 1)
