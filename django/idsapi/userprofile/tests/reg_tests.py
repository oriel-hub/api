import uuid

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase

from userprofile.models import UserProfile
import userprofile.admin

import unicodecsv
import StringIO

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
                'first_name': u'User',
                'last_name': u'1',
                'email': u'user1@example.org',
                'country': u'GB',
                'website_using_api': u'http://www.example.org/',
                'commercial': u'Commercial',
                'agree_to_licensing': True,
                }
        return self.client.post(reverse('edit_profile'), profile_data, follow=True)

    def test_profile_is_created_for_new_user(self):
        profile = self.user1.userprofile
        self.assertTrue(isinstance(profile, UserProfile))

    def test_login_page_has_register_link(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, reverse('django_registration_register'))

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

    def test_cannot_create_profile_without_agree_to_licensing(self):
        self.login()
        profile_data = {
                'first_name': u'User',
                'last_name': u'1',
                'email': u'user1@example.org',
                'country': u'GB',
                'website_using_api': u'http://www.example.org/',
                'commercial': u'Commercial',
                'agree_to_licensing': False,
                }
        response = self.client.post(reverse('edit_profile'), profile_data)
        # check we are still on the edit page
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'You must agree to')

    def test_minimum_info_to_create_profile(self):
        self.create_profile()
        self.user1.userprofile.refresh_from_db()
        profile = self.user1.userprofile
        self.assertEqual('GB', profile.country)

    def test_access_guid_is_created_on_profile_edit(self):
        profile = self.user1.userprofile
        self.assertEqual(0, len(profile.access_guid))
        self.create_profile()
        user = User.objects.get(username='user1')
        profile = user.userprofile
        self.assertEqual(36, len(profile.access_guid))

    def test_access_guid_is_not_regenerated_after_it_exists(self):
        profile = self.user1.userprofile
        orig_guid = profile.access_guid = str(uuid.uuid4())
        profile.beacon_guid = str(uuid.uuid4())
        profile.user_level = u'Partner'
        profile.save()
        self.create_profile()
        user = User.objects.get(username='user1')
        profile = user.userprofile
        self.assertEqual(orig_guid, profile.access_guid)
        self.assertEqual(u'Partner', profile.user_level)

    def test_profile_details_include_email(self):
        self.test_minimum_info_to_create_profile()
        response = self.client.get(reverse('profile_detail'))
        self.assertContains(response, 'user1@example.org')

    def test_profile_csv_download_requires_staff(self):
        self.login()
        response = self.client.get(
            reverse(userprofile.admin.download_view),
            follow=True
        )
        self.assertContains(response, 'Log in')

    def test_profile_csv_download_output(self):
        self.user1.is_staff = True
        self.user1.save()
        self.login()

        response = self.client.get(reverse(userprofile.admin.download_view))

        expected = StringIO.StringIO()
        writer = unicodecsv.writer(expected)
        writer.writerow(userprofile.admin.CSV_COL_NAMES)
        for user in User.objects.all():
            profile = user.userprofile
            writer.writerow([
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.is_staff,
                user.is_active,
                user.is_superuser,
                user.last_login,
                user.date_joined,
                profile.user_level,
                profile.organisation,
                profile.organisation_url,
                profile.organisation_address1,
                profile.organisation_address2,
                profile.organisation_address3,
                profile.city,
                profile.country,
                profile.zip_postal_code,
                profile.organisation_type,
                profile.api_usage_type,
                profile.cms_technology_platform,
                profile.heard_about,
                profile.website_using_api,
                profile.commercial,
                profile.agree_to_licensing,
                profile.access_guid,
                profile.beacon_guid,
                ])

        self.assertEqual(expected.getvalue(), response.content)
        self.assertEqual('text/csv', response['Content-Type'])
        self.assertEqual('attachment; filename=users.csv',
            response['Content-Disposition'])
