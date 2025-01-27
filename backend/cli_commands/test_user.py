from unittest.mock import patch
from .UserCommand import add_user, remove_user, change_password
from django.contrib.auth.models import User
from django.test import TestCase


class PasswordInputTests(TestCase):
    def setUp(self):
        super().setUp()
        self.patcher_getpass = patch(
            "cli_commands.UserCommand.getpass", return_value="test12345!"
        )
        self.patcher_validate = patch("cli_commands.UserCommand.validate_password")
        self.patcher_check = patch(
            "cli_commands.UserCommand.User.check_password", return_value=False
        )

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
            add_user("test_user")
            self.assertTrue(User.objects.filter(username="test_user").exists())
            self.assertIn("User 'test_user' added", log.output[0])
            self.assertEqual(self.mock_getpass.call_count, 2)
            self.assertEqual(self.mock_validate.call_count, 1)
            self.assertEqual(self.mock_check.call_count, 0)

    def test_remove_user(self):
        with self.assertLogs(level="INFO") as log:
            User.objects.create_user(username="test", password="test")
            remove_user("test")
            self.assertFalse(User.objects.filter(username="test").exists())
            self.assertIn("User 'test' removed", log.output[0])

    def test_change_password(self):
        with self.assertLogs(level="INFO") as log:
            User.objects.create_user(username="test_change", password="test")
            change_password("test_change")
            self.assertIn("changed successfully", log.output[0])
            self.assertEqual(self.mock_getpass.call_count, 2)
            self.assertEqual(self.mock_validate.call_count, 1)
            self.assertEqual(self.mock_check.call_count, 1)

            self.patcher_check.stop()

            # changing again to same password should not work
            change_password("test_change")
            self.assertIn("same as the old password", log.output[1])
            self.assertEqual(self.mock_getpass.call_count, 4)
            self.assertEqual(self.mock_validate.call_count, 2)
            self.assertEqual(self.mock_check.call_count, 1)
