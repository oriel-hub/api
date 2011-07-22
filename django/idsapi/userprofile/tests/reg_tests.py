import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from userprofile.models import UserProfile

class RegistrationTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', email='user1@example.org')
        self.user1.set_password('password')
        self.user1.save()

    def tearDown(self):
        self.user1.delete()

    def login(self):
        self.client.login(username='user1', password='password')

    def create_profile(self):
        self.login()
        profile_data = {
                'name': u'User 1',
                'email': u'user1@example.org',
                'country': u'GB',
                'website_using_api': u'http://www.example.org/',
                'commercial': u'Commercial',
                'agree_to_licensing': True,
                }
        return self.client.post(reverse('edit_profile'), profile_data, follow=True)

    def test_profile_is_created_for_new_user(self):
        profile = self.user1.get_profile()
        self.assertTrue(isinstance(profile, UserProfile))

    def test_redirected_to_edit_profile_on_first_login(self):
        self.login()
        response = self.client.get(reverse('profile_detail'))
        self.assertRedirects(response, reverse('edit_profile'))

    def test_edit_profile_form_includes_email(self):
        self.login()
        response = self.client.get(reverse('edit_profile'))
        self.assertContains(response, 'user1@example.org')

    def test_edit_profile_form_does_not_include_guid_fields(self):
        self.login()
        response = self.client.get(reverse('edit_profile'))
        self.assertNotContains(response, 'guid')
        self.assertNotContains(response, 'GUID')

    def test_minimum_info_to_create_profile(self):
        self.create_profile()
        profile = self.user1.get_profile()
        self.assertEqual('User 1', profile.name)

    def test_access_guid_is_created_on_profile_edit(self):
        profile = self.user1.get_profile()
        self.assertEqual(0, len(profile.access_guid))
        self.create_profile()
        user = User.objects.get(username='user1')
        profile = user.get_profile()
        self.assertEqual(36, len(profile.access_guid))

    def test_access_guid_is_not_regenerated_after_it_exists(self):
        profile = self.user1.get_profile()
        orig_guid = profile.access_guid = str(uuid.uuid4())
        profile.save()
        self.create_profile()
        user = User.objects.get(username='user1')
        profile = user.get_profile()
        self.assertEqual(orig_guid, profile.access_guid)

    def test_profile_details_include_email(self):
        self.test_minimum_info_to_create_profile()
        response = self.client.get(reverse('profile_detail'))
        self.assertContains(response, 'user1@example.org')


