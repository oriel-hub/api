# integration tests at the API level
from django.test.testcases import TestCase

import json

class ApiSearchIntegrationTests(TestCase):

    def undp_search(self, asset_type='assets', output_format='', content_type='application/json'):
        return self.client.get('/a/' + asset_type + '/search/' + output_format, 
                {'q': 'undp'}, ACCEPT=content_type)

    def test_id_only_search_returns_200(self):
        response = self.undp_search(output_format='id')
        self.assertEqual(200, response.status_code)

    def test_json_id_only_search_returns_only_ids(self):
        response = self.undp_search(output_format='id')
        search_results = json.loads(response.content)
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the id field
        for result in search_results:
            self.assertEqual(['id'], result.keys())

    def test_json_short_search_returns_short_fields(self):
        response = self.undp_search(output_format='short')
        search_results = json.loads(response.content)
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the correct field
        for result in search_results:
            sorted_keys = result.keys()
            sorted_keys.sort()
            self.assertEqual(['id', 'object_type', 'title'], sorted_keys)

    def test_json_full_search_returns_more_than_3_fields(self):
        response = self.undp_search(output_format='full')
        search_results = json.loads(response.content)
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the correct field
        for result in search_results:
            self.assertTrue(len(result.keys()) > 3)

    def test_blank_search_returns_same_as_short_search(self):
        response_short = self.undp_search(output_format='short')
        response_blank = self.undp_search(output_format='')
        self.assertEqual(response_short.content, response_blank.content)

    def test_400_returned_if_no_q_parameter(self):
        response = self.client.get('/a/assets/search/', ACCEPT='application/json')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_asset_type(self):
        response = self.undp_search(asset_type='foobars')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_output_format(self):
        response = self.undp_search(output_format='foobar')
        self.assertEqual(400, response.status_code)

    def test_document_search_returns_200(self):
        response = self.undp_search(asset_type='documents')
        self.assertEqual(200, response.status_code)

class ApiGetAssetIntegrationTests(TestCase):

    def get_asset(self, asset_type='assets', asset_id='1234', output_format='', content_type='application/json'):
        return self.client.get('/a/' + asset_type + '/' + asset_id + '/' + output_format, 
                {'q': 'undp'}, ACCEPT=content_type)

    def test_get_document_by_id_returns_200(self):
        response = self.get_asset(asset_type='documents')
        self.assertEqual(200, response.status_code)

    def test_get_asset_by_id_returns_200(self):
        response = self.get_asset()
        self.assertEqual(200, response.status_code)
