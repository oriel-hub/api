from django.contrib.auth.models import User

from openapi.tests.test_base import BaseTestCase
from openapi.tests.api_tests import ApiTestsBase

class ApiAuthTests(BaseTestCase):
    def test_403_returned_if_not_logged_in(self):
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'})
        self.assertEqual(403, response.status_code)

    def test_403_returned_if_user_not_active(self):
        self.login()
        self.user.is_active = False
        self.user.save()
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'})
        self.assertEqual(403, response.status_code)

    def test_search_works_with_normal_login(self):
        self.login()
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'})
        self.assertEqual(200, response.status_code)

    def test_search_works_with_token_in_header(self):
        profile = self.user.get_profile()
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'},
                HTTP_TOKEN_GUID=profile.access_guid)
        self.assertEqual(200, response.status_code)

    def test_search_works_with_token_in_url(self):
        profile = self.user.get_profile()
        response = self.client.get('/openapi/documents/search/', 
                {'q': 'undp', '_token_guid': profile.access_guid})
        self.assertEqual(200, response.status_code)

class UserLimitTests(ApiTestsBase):
    def test_200_returned_for_500_results_requested_general_user(self):
        profile = self.user.get_profile()
        profile.user_level = u'General User'
        profile.save()
        response = self.object_search(query={'q': 'un', 'num_results': '500'})
        self.assertEqual(200, response.status_code)

    def test_400_returned_if_more_than_500_results_requested_general_user(self):
        profile = self.user.get_profile()
        profile.user_level = u'General User'
        profile.save()
        response = self.object_search(query={'q': 'un', 'num_results': '501'})
        self.assertEqual(400, response.status_code)

    def test_200_returned_for_2000_results_requested_partner_user(self):
        profile = self.user.get_profile()
        profile.user_level = u'Partner'
        profile.save()
        response = self.object_search(query={'q': 'un', 'num_results': '2000'})
        self.assertEqual(200, response.status_code)

    def test_400_returned_if_more_than_2000_results_requested_partner_user(self):
        profile = self.user.get_profile()
        profile.user_level = u'Partner'
        profile.save()
        response = self.object_search(query={'q': 'un', 'num_results': '2001'})
        self.assertEqual(400, response.status_code)

    def test_200_returned_for_more_than_2000_results_requested_unlimited_user(self):
        profile = self.user.get_profile()
        profile.user_level = u'Unlimited'
        profile.save()
        response = self.object_search(query={'q': 'un', 'num_results': '2001'})
        self.assertEqual(200, response.status_code)

