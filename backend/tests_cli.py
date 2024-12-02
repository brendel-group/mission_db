from django.test import TestCase
from datetime import datetime
import cli


class CLITests(TestCase):
    def setUp(self):
        pass

    def test_extract_info_from_folder(self):
        date, name = cli.extract_info_from_folder("2024.11.30_test")
        self.assertEqual(date, datetime.strptime("2024.11.30", "%Y.%m.%d"))
        self.assertEqual(name, "test")
