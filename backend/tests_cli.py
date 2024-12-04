from django.test import TestCase
from datetime import date, datetime
from restapi.models import Mission, Tag
from restapi.serializer import MissionSerializer, TagSerializer
import cli
import logging
from io import StringIO
import sys


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
                other="other info",
            ).exists()
        )
        cli.add_mission_from_folder("2024.12.02_test_add_mission_2", other="other info")
        self.assertTrue(
            Mission.objects.filter(
                name="test_add_mission_2",
                date="2024-12-02",
                location=None,
                other="other info",
            ).exists()
        )

    def test_add_mission(self):
        cli.add_mission("TestAddMission", "2024-12-02")
        self.assertTrue(
            Mission.objects.filter(name="TestAddMission", date="2024-12-02").exists()
        )
        cli.add_mission("TestAddMission", "2024-12-02")
        self.assertEqual(
            len(Mission.objects.filter(name="TestAddMission", date="2024-12-02")), 2
        )
        cli.add_mission("TestAddMission", "2024-12-02", other="other")
        self.assertTrue(
            Mission.objects.filter(
                name="TestAddMission", date="2024-12-02", other="other"
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

    def test_print_mission_table(self):
        missions = [
            Mission.objects.create(name="Test", date="2024-12-02") for i in range(3)
        ]
        serializer = MissionSerializer(missions, many=True)
        cli.print_table(serializer.data)
        sys.stdout.flush()
        self.assertEqual(
            self.captured_output.getvalue().strip().replace(" ", "").replace("─", ""),
            "id│name│date│location│other\n"
            + "┼┼┼┼\n"
            + f"{missions[0].id}│Test│2024-12-02│None│None\n"
            + f"{missions[1].id}│Test│2024-12-02│None│None\n"
            + f"{missions[2].id}│Test│2024-12-02│None│None",
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
            "--other",
            "Test with all fields",
        ]
        with self.assertLogs(level="INFO") as log:
            cli.main(args)
            self.assertTrue(
                Mission.objects.filter(
                    name="Test",
                    date="2024-12-02",
                    location="Tübingen",
                    other="Test with all fields",
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
