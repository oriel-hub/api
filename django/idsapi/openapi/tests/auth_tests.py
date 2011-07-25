from django.contrib.auth.models import User

from openapi.tests.test_base import BaseTestCase

class ApiAuthTests(BaseTestCase):
    def test_403_returned_if_not_logged_in(self):
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'})
        self.assertEqual(403, response.status_code)

    def test_search_works_with_normal_login(self):
        self.login()
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'})
        self.assertEqual(200, response.status_code)

    def test_search_works_with_token_in_header(self):
        profile = self.user.get_profile()
        response = self.client.get('/openapi/documents/search/', {'q': 'undp'},
                TOKEN_GUID=profile.access_guid)
        self.assertEqual(200, response.status_code)

    def test_search_works_with_token_in_url(self):
        profile = self.user.get_profile()
        response = self.client.get('/openapi/documents/search/', 
                {'q': 'undp', '_token_guid': profile.access_guid})
        self.assertEqual(200, response.status_code)
