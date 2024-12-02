from django.test import TestCase
from datetime import date, datetime
from restapi.models import Mission
import cli
import logging


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
    def setUp(self):
        # disable logging
        self.logger = logging.getLogger()
        self.logger.disabled = True

    def tearDown(self):
        # reenable logging
        self.logger.disabled = False

    def test_validate_date(self):
        self.assertIsNone(cli.validate_date("Wrong format"))
        self.assertIsNone(cli.validate_date("2024-13-02"))

    def test_extract_info_from_folder(self):
        mission_date, name = cli.extract_info_from_folder("2024.13.30_test")
        self.assertIsNone(mission_date)
        self.assertIsNone(name)

    def test_add_mission_from_folder(self):
        cli.add_mission_from_folder("2024.13.02_test_add_mission")
        self.assertFalse(
            Mission.objects.filter(name="test_add_mission", date="2024-12-02").exists()
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
