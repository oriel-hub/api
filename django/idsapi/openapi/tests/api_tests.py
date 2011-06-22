# integration tests at the API level
from django.test.testcases import TestCase

import json
import re

from openapi.defines import URL_ROOT, asset_types

class ApiSearchTests(TestCase):

    def asset_search(self, asset_type='assets', output_format='full', query={'q':'undp'},
            content_type='application/json'):
        return self.client.get(URL_ROOT + asset_type + '/search/' + output_format, 
                query, ACCEPT=content_type)

class ApiSearchIntegrationTests(ApiSearchTests):

    def test_id_only_search_returns_200(self):
        response = self.asset_search(output_format='id')
        self.assertEqual(200, response.status_code)

    def test_json_id_only_search_returns_only_ids(self):
        response = self.asset_search(output_format='id')
        search_results = json.loads(response.content)['results']
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the id field
        for result in search_results:
            sorted_keys = result.keys()
            sorted_keys.sort()
            self.assertEqual(['id', 'metadata_url'], sorted_keys)

    def test_json_short_search_returns_short_fields(self):
        response = self.asset_search(output_format='short')
        search_results = json.loads(response.content)['results']
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the correct field
        for result in search_results:
            sorted_keys = result.keys()
            sorted_keys.sort()
            self.assertEqual(['id', 'metadata_url', 'object_type', 'title'], sorted_keys)

    def test_json_full_search_returns_more_than_3_fields(self):
        response = self.asset_search(output_format='full')
        search_results = json.loads(response.content)['results']
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the correct field
        for result in search_results:
            self.assertTrue(len(result.keys()) > 3)

    def test_json_full_search_does_not_contain_facet_fields(self):
        response = self.asset_search(output_format='full')
        search_results = json.loads(response.content)['results']
        for result in search_results:
            for key in result.keys():
                self.assertFalse(key.endswith('_facet'))

    def test_query_by_country(self):
        response = self.asset_search(query={'country':'namibia'})
        # no assert - if the above line throws an exception then the test fails
        search_results = json.loads(response.content)['results']
        for result in search_results:
            namibia_found = False
            for country in result['country_focus']:
                if country.strip().lower().startswith('namibia'):
                    angola_found = True
            self.assertTrue(angola_found)

    def test_query_by_country_and_free_text(self):
        response = self.asset_search(query={'q':'undp', 'country':'angola'})
        self.assertEqual(200, response.status_code)

    def test_query_by_each_query_term(self):
        query_term_list = [
                {'country': 'angola'},
                {'keyword': 'gender'},
                {'region': 'global'},
                {'sector': 'report'},
                {'source': 'bridge'},
                {'source': 'eldis'},
                {'subject': 'gdn'},
                {'theme': 'climate'},
                ]
        for query_term in query_term_list:
            response = self.asset_search(query=query_term)
            self.assertEqual(200, response.status_code)
            search_results = json.loads(response.content)
            self.assertTrue(search_results['metadata']['num_results'] > 0)


    def test_query_by_boolean_country_and_free_text(self):
        response = self.asset_search(query={'q':'undp', 'country':'angola&tanzania'})
        self.assertEqual(200, response.status_code)

    def test_query_by_country_with_and(self):
        response = self.asset_search(query={'country':'angola&namibia'})
        search_results = json.loads(response.content)['results']
        for result in search_results:
            angola_found = False
            namibia_found = False
            for country in result['country_focus']:
                if country.strip().lower().startswith('angola'):
                    angola_found = True
                if country.strip().lower().startswith('namibia'):
                    namibia_found = True
            self.assertTrue(angola_found and namibia_found)

    def test_query_by_country_with_or(self):
        response = self.asset_search(query={'country':'namibia|iran'})
        search_results = json.loads(response.content)['results']
        for result in search_results:
            namibia_found = False
            iran_found = False
            for country in result['country_focus']:
                if country.strip().lower().startswith('namibia'):
                    namibia_found = True
                if country.strip().lower().startswith('iran'):
                    iran_found = True
            self.assertTrue(namibia_found or iran_found)

    def test_search_response_has_metadata(self):
        response = self.asset_search()
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('num_results') and metadata.has_key('start_offset'))

    def test_blank_search_returns_same_as_short_search(self):
        response_short = self.asset_search(output_format='short')
        response_blank = self.asset_search(output_format='')
        self.assertEqual(response_short.content, response_blank.content)

    def test_urls_include_friendly_ids(self):
        response = self.asset_search()
        search_results = json.loads(response.content)['results']
        for result in search_results:
            url_bits = result['metadata_url'].split(URL_ROOT)[-1].split('/')
            # should now have something like ['documents', '1234', 'full', 'asdf']
            self.assertTrue(len(url_bits) == 4)
            self.assertTrue(url_bits[0] != 'assets')
            self.assertTrue(url_bits[0] in asset_types)
            self.assertTrue(url_bits[1].isdigit())
            self.assertTrue(url_bits[2] == 'full')
            self.assertTrue(re.match(r'^[-\w]+$', url_bits[3]) != None)
            self.assertFalse(url_bits[3].startswith('-'))
            self.assertFalse(url_bits[3].endswith('-'))

    def test_document_search_returns_200(self):
        response = self.asset_search(asset_type='documents')
        self.assertEqual(200, response.status_code)

    def test_all_document_search_returns_200(self):
        response = self.asset_search(query={'all':''})
        self.assertEqual(200, response.status_code)

    def test_200_returned_if_no_results(self):
        response = self.asset_search(query={'country':'NoddyLand'})
        self.assertEqual(200, response.status_code)
        # this test is just to check the search actually returned zero results
        search_results = json.loads(response.content)
        self.assertEqual(0, search_results['metadata']['num_results'])
        self.assertEqual(0, len(search_results['results']))

class ApiSearchErrorTests(ApiSearchTests):

    def test_400_returned_if_no_q_parameter(self):
        response = self.asset_search(query={})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_asset_type(self):
        response = self.asset_search(asset_type='foobars')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_output_format(self):
        response = self.asset_search(output_format='foobar')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_query_parameter(self):
        response = self.asset_search(query={'foo': 'bar'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_for_repeated_country_search(self):
        response = self.asset_search(query={'country':['namibia','angola']})
        self.assertContains(response, 'country', status_code=400)

    def test_query_by_country_with_both_or_and_and(self):
        response = self.asset_search(query={'country':'angola|iran&namibia'})
        self.assertEqual(400, response.status_code)
    
class ApiGetAssetIntegrationTests(TestCase):

    def get_asset(self, asset_type='assets', asset_id='12345', output_format='', 
                                content_type='application/json'):
        return self.client.get(URL_ROOT + asset_type + '/' + asset_id + '/' + output_format, 
                ACCEPT=content_type)

    def test_get_document_by_id_returns_200(self):
        response = self.get_asset(asset_type='documents')
        self.assertEqual(200, response.status_code)

    def test_get_asset_by_id_returns_200(self):
        response = self.get_asset()
        self.assertEqual(200, response.status_code)

    def test_404_returned_if_no_asset(self):
        response = self.get_asset(asset_id='1234567890')
        self.assertEqual(404, response.status_code)

    def test_400_returned_if_unknown_asset_type(self):
        response = self.get_asset(asset_type='foobars')
        self.assertEqual(400, response.status_code)


class ApiRootIntegrationTests(TestCase):
    def get_root(self):
        return self.client.get(URL_ROOT, ACCEPT='application/json')

    def test_root_url_returns_200(self):
        response = self.get_root()
        self.assertEqual(200, response.status_code)

    def test_root_url_contains_help_link(self):
        response = self.get_root()
        response_dict = json.loads(response.content)
        self.assertTrue(response_dict['help'].startswith('http://'))

