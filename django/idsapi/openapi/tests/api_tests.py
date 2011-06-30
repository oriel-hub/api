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
            self.assertTrue(' '.join(result['country_focus']).lower().find('namibia') > -1)

    def test_query_by_country_and_free_text(self):
        response = self.asset_search(query={'q':'undp', 'country':'angola'})
        self.assertEqual(200, response.status_code)

    def test_query_by_each_query_term(self):
        query_term_list = [
                {'country': 'angola'},
                {'keyword': 'gender'},
                {'region': 'africa'},
                {'sector': 'report'},
                {'branch': 'bridge'},
                {'branch': 'eldis'},
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
            self.assertTrue(' '.join(result['country_focus']).lower().find('angola'))
            self.assertTrue(' '.join(result['country_focus']).lower().find('namibia'))

    def test_query_by_country_with_or(self):
        response = self.asset_search(query={'country':'namibia|iran'})
        search_results = json.loads(response.content)['results']
        for result in search_results:
            namibia_found = ' '.join(result['country_focus']).lower().find('namibia') > -1
            iran_found = ' '.join(result['country_focus']).lower().find('iran') > -1
            self.assertTrue(namibia_found or iran_found)

    def test_search_response_has_metadata(self):
        response = self.asset_search()
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('num_results') and metadata.has_key('start_offset'))

    def test_search_response_has_next_in_metadata(self):
        response = self.asset_search()
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('next_page'))
        self.assertTrue(metadata['next_page'].find('num_results') > -1)
        self.assertTrue(metadata['next_page'].find('start_offset') > -1)
        # also, default search should not have prev_page link
        self.assertFalse(metadata.has_key('prev_page'))

    def test_2nd_page_has_prev_in_metadata(self):
        response = self.asset_search(query={'q': 'undp', 'start_offset': '10'})
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('prev_page'))
        self.assertTrue(metadata['prev_page'].find('num_results') > -1)
        self.assertTrue(metadata['prev_page'].find('start_offset') > -1)

    def test_prev_never_has_negative_start_offset(self):
        response = self.asset_search(query={'q': 'undp', 'start_offset': '1'})
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('prev_page'))
        match = re.search(r'start_offset=([-0-9]+)', metadata['prev_page'])
        self.assertTrue(int(match.group(1)) >= 0)

    def test_num_results_in_query_matches_results_returned(self):
        response = self.asset_search(query={'q': 'undp', 'num_results': '20'})
        results = json.loads(response.content)['results']
        self.assertEqual(20, len(results))

    def test_num_results_correctly_passed_on_to_next_and_prev_links(self):
        response = self.asset_search(
                query={'q': 'undp', 'num_results': '20', 'start_offset': '20'})
        metadata = json.loads(response.content)['metadata']
        for link in ('prev_page', 'next_page'):
            match = re.search(r'num_results=([-0-9]+)', metadata[link])
            self.assertTrue(int(match.group(1)) == 20)

    def test_blank_search_returns_same_as_short_search(self):
        response_short = self.asset_search(output_format='short')
        response_blank = self.asset_search(output_format='')
        # the metadata is different due to next/prev link containing "short",
        # or not, so just compare up to the metadata.
        response_short = response_short.content.split('"metadata":')[0]
        response_blank = response_blank.content.split('"metadata":')[0]
        self.assertEqual(response_short, response_blank)

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

    def test_all_document_search_returns_400(self):
        response = self.asset_search(query={'all':''})
        self.assertEqual(400, response.status_code)

    def test_200_returned_if_no_results(self):
        response = self.asset_search(query={'country':'NoddyLand'})
        self.assertEqual(200, response.status_code)
        # this test is just to check the search actually returned zero results
        search_results = json.loads(response.content)
        self.assertEqual(0, search_results['metadata']['num_results'])
        self.assertEqual(0, len(search_results['results']))

    def test_200_returned_for_trailing_star(self):
        response = self.asset_search(query={'keyword': 'af*'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_middle_star(self):
        response = self.asset_search(query={'keyword': 'af*ca'})
        self.assertEqual(200, response.status_code)

    def test_200_returned_for_metadata_published_before(self):
        response = self.asset_search(query={'metadata_published_before': '2008-12-31'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_metadata_published_after(self):
        response = self.asset_search(query={'metadata_published_after': '2008-12-31'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_metadata_published_year(self):
        response = self.asset_search(query={'metadata_published_year': '2008'})
        self.assertEqual(200, response.status_code)
    
    def test_document_specific_query_param_author(self):
        response = self.asset_search(asset_type='documents', query={'author': 'john'})
        self.assertEqual(200, response.status_code)
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(' '.join(result['author']).lower().find('john') > -1)
        
    def test_organisation_specific_query_param_acronym(self):
        response = self.asset_search(asset_type='organisations', query={'acronym': 'UN*'})
        self.assertEqual(200, response.status_code)
        search_results = json.loads(response.content)['results']
        for result in search_results:
            acronym_found = result['acronym'].lower().find('un') > -1
            alternative_acronym_found = False
            if result.has_key('alternative_acronym'):
                alternative_acronym_found = ' '.join(result['alternative_acronym']).lower().find('un') > -1
            self.assertTrue(acronym_found or alternative_acronym_found)
        
    def test_item_specific_query_param_item_type(self):
        response = self.asset_search(asset_type='items', query={'item_type': 'Other*'})
        self.assertEqual(200, response.status_code)
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(result['item_type'].lower().find('other') > -1)
        
    def test_200_returned_for_document_published_before(self):
        response = self.asset_search(query={'document_published_before': '2008-12-31'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_document_published_after(self):
        response = self.asset_search(query={'document_published_after': '2008-12-31'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_document_published_year(self):
        response = self.asset_search(query={'document_published_year': '2008'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_item_dates(self):
        for query_param in ['item_started_after', 'item_started_before', 'item_finished_after',
                'item_finished_before']:
            response = self.asset_search(query={query_param: '2008-12-31'})
            self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_item_years(self):
        for query_param in ['item_started_year', 'item_finished_year',]:
            response = self.asset_search(query={query_param: '2008'})
            self.assertEqual(200, response.status_code)

    def test_num_results_only_returns_only_num_results(self):
        response = self.asset_search(query={'q': 'undp', 'num_results_only': None})
        self.assertEqual(200, response.status_code)
        response_dict = json.loads(response.content)
        self.assertTrue(response_dict.has_key('metadata'))
        self.assertFalse(response_dict.has_key('results'))
        self.assertEqual(1, len(response_dict['metadata'].keys()))
        self.assertTrue(response_dict['metadata'].has_key('num_results'))
    

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

    def test_400_returned_for_leading_star(self):
        response = self.asset_search(query={'keyword': '*ca'})
        self.assertEqual(400, response.status_code)
    
    def test_400_returned_for_metadata_published_before_bad_date_format(self):
        bad_dates = ['200-12-31', '2008-1-01', '2008-01-1', '20080101', '200A-01-01']
        for date in bad_dates:
            response = self.asset_search(query={'metadata_published_before': date})
            self.assertEqual(400, response.status_code)

    def test_400_returned_for_metadata_published_year_bad_date_format(self):
        bad_dates = ['200', '200A', '20080',]
        for date in bad_dates:
            response = self.asset_search(query={'metadata_published_year': date})
            self.assertEqual(400, response.status_code)

    def test_400_returned_for_bad_date_query_param_prefix(self):
        response = self.asset_search(query={'foobar_published_year': '2009'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_for_bad_date_query_param_postfix(self):
        response = self.asset_search(query={'metadata_published_foobar': '2009'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_document_specific_query_param_used(self):
        response = self.asset_search(query={'author': 'John'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_more_than_500_results_requested(self):
        response = self.asset_search(query={'q': 'undp', 'num_results': '501'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_num_results_is_negative(self):
        response = self.asset_search(query={'q': 'undp', 'num_results': '-1'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_start_offset_is_negative(self):
        response = self.asset_search(query={'q': 'undp', 'start_offset': '-1'})
        self.assertEqual(400, response.status_code)

class ApiGetAllIntegrationTests(TestCase):

    def get_all(self, asset_type='assets', output_format='', 
                                content_type='application/json'):
        return self.client.get(URL_ROOT + asset_type + '/all/' + output_format, 
                ACCEPT=content_type)
    
    def test_get_all_documents_returns_200(self):
        response = self.get_all(asset_type='documents')
        self.assertEqual(200, response.status_code)

    def test_get_all_assets_returns_200(self):
        response = self.get_all()
        self.assertEqual(200, response.status_code)

    def test_400_returned_if_unknown_asset_type(self):
        response = self.get_all(asset_type='foobars')
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

class ApiFieldListIntegrationTests(TestCase):
    def get_field_list(self):
        return self.client.get(URL_ROOT + 'fieldlist/', ACCEPT='application/json')

    def test_field_list_returns_200(self):
        response = self.get_field_list()
        self.assertEqual(200, response.status_code)

    def test_field_list_has_items(self):
        response = self.get_field_list()
        response_list = json.loads(response.content)
        self.assertTrue(len(response_list) > 1)

class ApiFacetIntegrationTests(TestCase):
    def facet_search(self, asset_type='assets', facet_type='country', query={'q':'undp'},
            content_type='application/json'):
        return self.client.get(URL_ROOT + asset_type + '/' + facet_type + '_count/', 
                query, ACCEPT=content_type)

    def test_200_returned_for_all_facet_types(self):
        for facet_type in ('country', 'region', 'keyword', 'sector', 'subject', 'theme'):
            response = self.facet_search(facet_type=facet_type)
            self.assertEqual(200, response.status_code)

    def test_200_returned_for_individual_asset_type(self):
        response = self.facet_search(asset_type='documents')
        self.assertEqual(200, response.status_code)
            
    def test_400_returned_if_unknown_facet_type(self):
        response = self.facet_search(facet_type='foobars')
        self.assertEqual(400, response.status_code)
                
    def test_all_counts_from_facet_gt_0(self):
        response = self.facet_search()
        search_results = json.loads(response.content)
        for country_count in search_results['country_count']:
            self.assertTrue(isinstance(country_count[0], unicode))
            self.assertTrue(isinstance(country_count[1], int))

class ApiCategoryChildrenIntegrationTests(TestCase):
    def children_search(self, asset_type='themes', asset_id=34,
            content_type='application/json'):
        return self.client.get(URL_ROOT + asset_type + '/' + str(asset_id) + '/children/full', 
                ACCEPT=content_type)
    
    def test_200_returned_for_children_search(self):
        child_searches = {'themes': 34, 'itemtypes': 1067} 
        for asset_type, asset_id in child_searches.items():
            response = self.children_search(asset_type=asset_type, asset_id=asset_id)
            self.assertEqual(200, response.status_code)

    def test_parents_match_for_children_search(self):
        response = self.children_search()
        search_results = json.loads(response.content)
        for result in search_results['results']:
            self.assertEqual(34, int(result['cat_parent']))
            
    def test_400_returned_for_invalid_child(self):
        response = self.children_search(asset_type='documents', asset_id=8346)
        self.assertEqual(400, response.status_code)