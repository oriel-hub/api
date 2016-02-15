# functions to help the tests
from django.contrib.auth.models import User
from django.test.testcases import TestCase

class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user1', email='user1@example.org')
        self.user.set_password('password')
        self.user.save()
        self.user = User.objects.get(username='user1')
        profile = self.user.userprofile
        profile.ensure_hidden_fields_set()
        profile.user_level = 'Partner'
        profile.save()

    def setUserLevel(self, level):
        profile = self.user.userprofile
        profile.user_level = level
        profile.save()

    def tearDown(self):
        self.user.delete()

    def login(self):
        self.client.login(username='user1', password='password')

