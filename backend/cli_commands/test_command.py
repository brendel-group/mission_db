import sys
from io import StringIO
from django.test import TestCase
from restapi.models import Mission, Tag
from restapi.serializer import MissionSerializer, TagSerializer
from cli_commands.Command import Command
from datetime import date


class TableTests(TestCase):
    def setUp(self):
        self.mission = Mission.objects.create(name="TestRemove", date=date.today())
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = self.captured_output

    def tearDown(self):
        self.mission.delete()
        sys.stdout = self.original_stdout

    def test_print_mission_table(self):
        missions = [
            Mission.objects.create(name=f"Test{i}", date="2024-12-02") for i in range(3)
        ]
        serializer = MissionSerializer(missions, many=True)
        Command.print_table(serializer.data)
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
        Command.print_table(serializer.data)
        sys.stdout.flush()
        self.assertEqual(
            self.captured_output.getvalue().strip().replace(" ", "").replace("─", ""),
            "id│name│color\n"
            + "┼┼\n"
            + f"{tags[0].id}│{tags[0].name}│#FFFFFF\n"
            + f"{tags[1].id}│{tags[1].name}│#FFFFFF\n"
            + f"{tags[2].id}│{tags[2].name}│#FFFFFF",
        )
