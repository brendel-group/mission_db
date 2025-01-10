from django.test import TestCase
from rest_framework_api_key.models import APIKey
from cli_commands.ApiKeyCommand import add_api_key, remove_api_key


class APIKeyTests(TestCase):
    def setUp(self):
        APIKey.objects.create_key(name="Test")
        self.key = APIKey.objects.get(name="Test")

    def test_add_key(self):
        with self.assertLogs(level="INFO") as log:
            add_api_key(name="Test2")
            self.assertTrue(APIKey.objects.filter(name="Test2").exists())
            self.assertIn("Test2", log.output[0])
            self.assertIn("key: ", log.output[0])

    def test_remove_key(self):
        with self.assertLogs(level="INFO") as log:
            remove_api_key(name=self.key.name)
            self.assertFalse(APIKey.objects.filter(name=self.key.name).exists())
            self.assertIn(self.key.name, log.output[0])
            self.assertIn("Removed", log.output[0])
