from django.test import TestCase
from datetime import date
from restapi.models import Mission, Tag
from restapi.serializer import MissionSerializer
from cli_commands.Command import Command
import cli
from io import StringIO
import sys


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
        Command.print_table(serializer.data)
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
