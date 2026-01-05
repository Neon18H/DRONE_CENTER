from django.test import Client, TestCase
from django.urls import reverse


class SmokeTests(TestCase):
    def test_login_page(self):
        client = Client()
        response = client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
