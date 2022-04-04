from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import reverse

# Create your tests here.


class HomePageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):  # new
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):  # new
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "rsvp/home.html")

    def test_template_content(self):  # new
        response = self.client.get(reverse("home"))
        self.assertContains(response, "<h1>Hello world!</h1>")


class SearchPathPageTests(SimpleTestCase):
    def test_url_exists_at_correct_location(self):
        response = self.client.get("/search_path.html")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):  # new
        response = self.client.get(reverse("search_path"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):  # new
        response = self.client.get(reverse("search_path"))
        self.assertTemplateUsed(response, "rsvp/search_path.html")

    def test_template_content(self):  # new
        response = self.client.get(reverse("search_path"))
        self.assertContains(response, "<h1>Search Path</h1>")