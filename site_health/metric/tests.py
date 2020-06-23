from django.test import TestCase

from site_health.users.models import User
from site_health.website.models import *


class BaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create()
        self.site = Site.objects.create(url="https://simonnouwens.nl", owner=self.user)
        self.page = Page.simple_factory(self.site, "/")


class AnimalTestCase(BaseTest):
    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        lion = Animal.objects.get(name="lion")
        cat = Animal.objects.get(name="cat")
        self.assertEqual(lion.speak(), 'The lion says "roar"')
        self.assertEqual(cat.speak(), 'The cat says "meow"')
