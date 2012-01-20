# integration tests at the API level
import json, re, datetime

from django.conf import settings

from openapi import defines
from openapi.tests.test_base import BaseTestCase

class ApiTestsBase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.login()

    def object_search(self, object_type='assets', output_format='full', query=None,
            content_type='application/json'):
        if query == None:
            query = {'q':'undp'}
        if output_format == 'no_slash':
            output_format = ''
        else:
            output_format = '/' + output_format
        return self.client.get(defines.URL_ROOT + object_type + '/search' + output_format, 
                query, ACCEPT=content_type)

    def get_all(self, object_type='assets', output_format='', query=None,
                                content_type='application/json'):
        if query == None:
            query = {}
        return self.client.get(defines.URL_ROOT + object_type + '/all/' + output_format, 
                query, ACCEPT=content_type)
    
class ApiSearchResponseTests(ApiTestsBase):

    def test_id_only_search_returns_200(self):
        response = self.object_search(output_format='id')
        self.assertEqual(200, response.status_code)

    def test_json_id_only_search_returns_only_ids(self):
        response = self.object_search(output_format='id')
        search_results = json.loads(response.content)['results']
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the id field
        for result in search_results:
            sorted_keys = result.keys()
            sorted_keys.sort()
            self.assertEqual(['metadata_url', 'object_id'], sorted_keys)

    def test_json_short_search_returns_short_fields(self):
        response = self.object_search(output_format='short')
        search_results = json.loads(response.content)['results']
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the correct field
        for result in search_results:
            sorted_keys = result.keys()
            sorted_keys.sort()
            self.assertEqual(['metadata_url', 'object_id', 'object_type', 'title'], sorted_keys)

    def test_json_full_search_returns_more_than_3_fields(self):
        response = self.object_search(output_format='full')
        search_results = json.loads(response.content)['results']
        # no assert - if the above line throws an exception then the test fails
        # check that the results only contain the correct field
        for result in search_results:
            self.assertTrue(len(result.keys()) > 3)

    def test_json_full_search_does_not_contain_facet_fields(self):
        response = self.object_search(output_format='full')
        search_results = json.loads(response.content)['results']
        for result in search_results:
            for key in result.keys():
                self.assertFalse(key.endswith('_facet'))

    def test_json_full_search_does_not_contain_hidden_fields(self):
        response = self.object_search(output_format='full')
        search_results = json.loads(response.content)['results']
        for result in search_results:
            for key in result.keys():
                self.assertFalse(key in settings.ADMIN_ONLY_FIELDS)

    def test_can_specify_content_type_in_query(self):
        response = self.object_search(query={'q': 'undp', '_accept': 'application/json'},
                content_type='text/html')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response['Content-Type'].lower(), 'application/json')

    def test_assets_search_contains_only_assets(self):
        response = self.object_search(output_format='short', 
                query={'q': 'Agricultural', 'num_results': '500'})
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(result['object_type'] in defines.ASSET_NAMES)

    def test_long_abstract_contains_image_beacon(self):
        response = self.object_search(object_type='documents', output_format='full')
        search_results = json.loads(response.content)['results']
        profile = self.user.get_profile()
        for result in search_results:
            if result.has_key('long_abstract'):
                self.assertTrue(result['long_abstract'].find(settings.IMAGE_BEACON_STUB_URL) > -1)
                self.assertTrue(result['long_abstract'].find(profile.beacon_guid) > -1)

    def test_long_abstract_truncated_for_general_user(self):
        self.setUserLevel('General User')
        response = self.object_search(object_type='documents', output_format='full')
        search_results = json.loads(response.content)['results']
        for result in search_results:
            if result.has_key('long_abstract'):
                abstract_without_beacon = result['long_abstract'].split('<img')[0]
                self.assertTrue(250 >= len(abstract_without_beacon))

    def test_long_abstract_does_not_contain_image_beacon_for_unlimited_user(self):
        self.setUserLevel('Unlimited')
        response = self.object_search(object_type='documents', output_format='full')
        search_results = json.loads(response.content)['results']
        for result in search_results:
            if result.has_key('long_abstract'):
                self.assertTrue(result['long_abstract'].find(settings.IMAGE_BEACON_STUB_URL) == -1)

class ApiSearchIntegrationTests(ApiTestsBase):

    def test_query_by_country(self):
        response = self.object_search(query={'country':'namibia'})
        # no assert - if the above line throws an exception then the test fails
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(' '.join(result['country_focus']).lower().find('namibia') > -1)

    def test_query_by_country_and_free_text(self):
        response = self.object_search(query={'q':'undp', 'country':'angola'})
        self.assertEqual(200, response.status_code)

    def test_query_by_each_query_term(self):
        query_term_list = [
                {'country': 'angola'},
                {'keyword': 'gender'},
                {'region': 'africa'},
                {'sector': 'report'},
                {'site': 'bridge'},
                {'site': 'eldis'},
                {'subject': 'gdn'},
                {'theme': 'climate'},
                ]
        for query_term in query_term_list:
            response = self.object_search(query=query_term)
            self.assertEqual(200, response.status_code)
            search_results = json.loads(response.content)
            self.assertTrue(search_results['metadata']['total_results'] > 0)

    def test_query_by_boolean_country_and_free_text(self):
        response = self.object_search(query={'q':'undp', 'country':'angola&tanzania'})
        self.assertEqual(200, response.status_code)

    def test_query_by_country_with_and(self):
        response = self.object_search(query={'country':'angola&namibia'})
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(' '.join(result['country_focus']).lower().find('angola') > -1)
            self.assertTrue(' '.join(result['country_focus']).lower().find('namibia') > -1)

    def test_query_by_country_with_or(self):
        response = self.object_search(query={'country':'namibia|iran'})
        search_results = json.loads(response.content)['results']
        for result in search_results:
            namibia_found = ' '.join(result['country_focus']).lower().find('namibia') > -1
            iran_found = ' '.join(result['country_focus']).lower().find('iran') > -1
            self.assertTrue(namibia_found or iran_found)

    def test_blank_search_returns_same_as_short_search(self):
        response_short = self.object_search(output_format='short')
        response_blank = self.object_search(output_format='')
        response_no_slash = self.object_search(output_format='no_slash')
        # the metadata is different due to next/prev link containing "short",
        # or not, so just compare up to the metadata.
        response_short = response_short.content.split('"metadata":')[0]
        response_blank = response_blank.content.split('"metadata":')[0]
        response_no_slash = response_no_slash.content.split('"metadata":')[0]
        self.assertEqual(response_short, response_blank)
        self.assertEqual(response_short, response_no_slash)

    def test_urls_include_friendly_ids(self):
        response = self.object_search()
        search_results = json.loads(response.content)['results']
        for result in search_results:
            url_bits = result['metadata_url'].split(defines.URL_ROOT)[-1].strip('/').split('/')
            # should now have something like ['documents', '1234', 'full', 'asdf']
            self.assertTrue(len(url_bits) == 4)
            self.assertTrue(url_bits[0] != 'assets')
            self.assertTrue(url_bits[0] in defines.OBJECT_TYPES)
            self.assertTrue(re.match(r'^[AC]\d+$', url_bits[1]) != None)
            self.assertTrue(url_bits[2] == 'full')
            self.assertTrue(re.match(r'^[-\w]+$', url_bits[3]) != None)
            self.assertFalse(url_bits[3].startswith('-'))
            self.assertFalse(url_bits[3].endswith('-'))

    def test_document_search_returns_200(self):
        response = self.object_search(object_type='documents')
        self.assertEqual(200, response.status_code)

    def test_all_document_search_returns_400(self):
        response = self.object_search(query={'all':''})
        self.assertEqual(400, response.status_code)

    def test_200_returned_if_no_results(self):
        response = self.object_search(query={'country':'NoddyLand'})
        self.assertEqual(200, response.status_code)
        # this test is just to check the search actually returned zero results
        search_results = json.loads(response.content)
        self.assertEqual(0, search_results['metadata']['total_results'])
        self.assertEqual(0, len(search_results['results']))

    def test_200_returned_for_trailing_star(self):
        response = self.object_search(query={'keyword': 'af*'})
        self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_middle_star(self):
        response = self.object_search(query={'keyword': 'af*ca'})
        self.assertEqual(200, response.status_code)

    def test_document_specific_query_param_author(self):
        response = self.object_search(object_type='documents', query={'author': 'john'})
        self.assertEqual(200, response.status_code)
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(' '.join(result['author']).lower().find('john') > -1)
        
    def test_organisation_specific_query_param_acronym(self):
        response = self.object_search(object_type='organisations', query={'acronym': 'UN*'})
        self.assertEqual(200, response.status_code)
        self.assertTrue(0 < json.loads(response.content)['metadata']['total_results'])
        search_results = json.loads(response.content)['results']
        for result in search_results:
            acronym_found = result['acronym'].lower().find('un') > -1
            alternative_acronym_found = False
            if result.has_key('alternative_acronym'):
                alternative_acronym_found = ' '.join(result['alternative_acronym']).lower().find('un') > -1
            self.assertTrue(acronym_found or alternative_acronym_found)
        
    def test_item_specific_query_param_item_type(self):
        response = self.object_search(object_type='items', query={'item_type': 'Other*'})
        self.assertEqual(200, response.status_code)
        self.assertTrue(0 < json.loads(response.content)['metadata']['total_results'])
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(result['item_type'].lower().find('other') > -1)
        
    def test_num_results_only_returns_only_total_results(self):
        response = self.object_search(query={'q': 'undp', 'num_results_only': None})
        self.assertEqual(200, response.status_code)
        response_dict = json.loads(response.content)
        self.assertTrue(response_dict.has_key('metadata'))
        self.assertFalse(response_dict.has_key('results'))
        self.assertEqual(1, len(response_dict['metadata'].keys()))
        self.assertTrue(response_dict['metadata'].has_key('total_results'))
    
    def test_extra_fields_with_object_search(self):
        response = self.object_search(object_type='documents', output_format='short',
                query={'q': 'undp', 'extra_fields': 'long_abstract'})
        # not all the results have the abstracts, so just check it doesn't
        # immediately complain
        self.assertEqual(200, response.status_code)

    def test_search_is_case_insensitive(self):
        response_upper = self.object_search(object_type='documents', query={'q': 'AGRI*'})
        response_upper_data = json.loads(response_upper.content)
        response_lower = self.object_search(object_type='documents', query={'q': 'agri*'})
        response_lower_data = json.loads(response_lower.content)
        self.assertEqual(response_upper_data['metadata']['total_results'],
                response_lower_data['metadata']['total_results'])

    def test_search_has_default_site_eldis(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'un', 'num_results': '500'})
        results = json.loads(response.content)['results']
        for result in results:
            self.assertEqual('eldis', result['site'])

class ApiPaginationTests(ApiTestsBase):

    def test_search_response_has_metadata(self):
        response = self.object_search()
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('total_results') and metadata.has_key('start_offset'))

    def test_search_response_has_next_in_metadata(self):
        response = self.object_search()
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('next_page'))
        self.assertTrue(metadata['next_page'].find('num_results') > -1)
        self.assertTrue(metadata['next_page'].find('start_offset') > -1)
        # also, default search should not have prev_page link
        self.assertFalse(metadata.has_key('prev_page'))

    def test_2nd_page_has_prev_in_metadata(self):
        response = self.object_search(query={'q': 'undp', 'start_offset': '10'})
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('prev_page'))
        self.assertTrue(metadata['prev_page'].find('num_results') > -1)
        self.assertTrue(metadata['prev_page'].find('start_offset') > -1)

    def test_prev_never_has_negative_start_offset(self):
        response = self.object_search(query={'q': 'undp', 'start_offset': '1'})
        metadata = json.loads(response.content)['metadata']
        self.assertTrue(metadata.has_key('prev_page'))
        match = re.search(r'start_offset=([-0-9]+)', metadata['prev_page'])
        self.assertTrue(int(match.group(1)) >= 0)

    def test_num_results_in_query_matches_results_returned(self):
        response = self.object_search(query={'q': 'undp', 'num_results': '20'})
        results = json.loads(response.content)['results']
        self.assertEqual(20, len(results))

    def test_num_results_correctly_passed_on_to_next_and_prev_links(self):
        response = self.object_search(
                query={'q': 'undp', 'num_results': '20', 'start_offset': '20'})
        metadata = json.loads(response.content)['metadata']
        for link in ('prev_page', 'next_page'):
            match = re.search(r'num_results=([-0-9]+)', metadata[link])
            self.assertTrue(int(match.group(1)) == 20)

class ApiDateQueryTests(ApiTestsBase):

    def test_200_returned_for_document_published_before(self):
        response = self.object_search(query={'document_published_before': '2008-12-31'})
        query_date = datetime.datetime.strptime('2008-12-31', "%Y-%m-%d")
        results = json.loads(response.content)['results']
        for result in results:
            document_published = datetime.datetime.strptime(
                    result['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(document_published < query_date)
    
    def test_200_returned_for_document_published_after(self):
        response = self.object_search(query={'document_published_after': '2008-12-31'})
        query_date = datetime.datetime.strptime('2008-12-31', "%Y-%m-%d")
        results = json.loads(response.content)['results']
        for result in results:
            document_published = datetime.datetime.strptime(
                    result['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(document_published >= query_date)
    
    def test_200_returned_for_document_published_year(self):
        response = self.object_search(query={'document_published_year': '2008'})
        results = json.loads(response.content)['results']
        for result in results:
            document_published = datetime.datetime.strptime(
                    result['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertEqual(2008, document_published.year)
    
    def test_200_returned_for_item_dates(self):
        for query_param in ['item_started_after', 'item_started_before', 'item_finished_after',
                'item_finished_before']:
            response = self.object_search(query={query_param: '2008-12-31'})
            self.assertEqual(200, response.status_code)
    
    def test_200_returned_for_item_years(self):
        for query_param in ['item_started_year', 'item_finished_year',]:
            response = self.object_search(query={query_param: '2008'})
            self.assertEqual(200, response.status_code)

    def test_400_returned_for_document_published_before_bad_date_format(self):
        bad_dates = ['200-12-31', '2008-1-01', '2008-01-1', '20080101', '200A-01-01']
        for date in bad_dates:
            response = self.object_search(object_type='documents', query={'document_published_before': date})
            self.assertEqual(400, response.status_code)

    def test_400_returned_for_document_published_year_bad_date_format(self):
        bad_dates = ['200', '200A', '20080',]
        for date in bad_dates:
            response = self.object_search(object_type='documents', query={'document_published_year': date})
            self.assertEqual(400, response.status_code)

class ApiSearchSortTests(ApiTestsBase):

    def test_sort_ascending_by_publication_date(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'undp', 'sort_asc': 'publication_date'})
        results = json.loads(response.content)['results']
        for i in range(9):
            date1 = datetime.datetime.strptime(results[i]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            date2 = datetime.datetime.strptime(results[i+1]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(date1 <= date2)

    def test_sort_descending_by_publication_date(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'undp', 'sort_desc': 'publication_date'})
        results = json.loads(response.content)['results']
        for i in range(9):
            date1 = datetime.datetime.strptime(results[i]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            date2 = datetime.datetime.strptime(results[i+1]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(date1 >= date2)

    def test_400_returned_for_disallowed_sort_field(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'undp', 'sort_asc': 'long_abstract'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_for_unknown_sort_field(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'undp', 'sort_desc': 'foobar'})
        self.assertEqual(400, response.status_code)

class ApiSearchErrorTests(ApiTestsBase):

    def test_400_returned_if_no_q_parameter(self):
        response = self.object_search(query={})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_object_type(self):
        response = self.object_search(object_type='foobars')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_output_format(self):
        response = self.object_search(output_format='foobar')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_query_parameter(self):
        response = self.object_search(query={'foo': 'bar'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_query_parameter_has_no_value(self):
        response = self.object_search(query={'country': ''})
        self.assertEqual(400, response.status_code)

    def test_404_returned_for_unknown_path(self):
        response = self.client.get('/openapi/foobar')
        self.assertEqual(404, response.status_code)

    # TODO: fails - framework bug? think about this ...
    #def test_406_returned_if_unknown_return_format(self):
    #    response = self.object_search(content_type='application/foobar')
    #    self.assertEqual(406, response.status_code)

    def test_405_returned_for_post_method_not_allowed(self):
        response = self.client.post(defines.URL_ROOT + 'assets/search/',
                {'q': 'undp'}, ACCEPT='application/json')
        self.assertEqual(405, response.status_code)

    def test_400_returned_for_repeated_country_search(self):
        response = self.object_search(query={'country':['namibia','angola']})
        self.assertContains(response, 'country', status_code=400)

    def test_query_by_country_with_both_or_and_and(self):
        response = self.object_search(query={'country':'angola|iran&namibia'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_for_leading_star(self):
        response = self.object_search(query={'keyword': '*ca'})
        self.assertEqual(400, response.status_code)
    
    def test_400_returned_for_bad_date_query_param_prefix(self):
        response = self.object_search(query={'foobar_published_year': '2009'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_for_bad_date_query_param_postfix(self):
        response = self.object_search(object_type='documents', query={'document_published_foobar': '2009'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_document_specific_query_param_used(self):
        response = self.object_search(query={'author': 'John'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_num_results_is_negative(self):
        response = self.object_search(query={'q': 'undp', 'num_results': '-1'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_start_offset_is_negative(self):
        response = self.object_search(query={'q': 'undp', 'start_offset': '-1'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_num_results_is_non_numeric(self):
        response = self.object_search(query={'q': 'undp', 'num_results': 'not_a_number'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_start_offset_is_non_numeric(self):
        response = self.object_search(query={'q': 'undp', 'start_offset': 'not_a_number'})
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_sort_asc_and_sort_desc_used(self):
        response = self.object_search(query={
            'q': 'undp', 
            'sort_asc': 'publication_date', 
            'sort_desc': 'object_id'
            })
        self.assertEqual(400, response.status_code)

class ApiGetAllIntegrationTests(ApiTestsBase):

    def test_get_all_documents_returns_200(self):
        response = self.get_all(object_type='documents')
        self.assertEqual(200, response.status_code)

    def test_get_all_assets_returns_200(self):
        response = self.get_all()
        self.assertEqual(200, response.status_code)

    def test_400_returned_if_unknown_object_type(self):
        response = self.get_all(object_type='foobars')
        self.assertEqual(400, response.status_code)

    def test_extra_fields_with_all_assets(self):
        response = self.get_all(object_type='documents', 
                query={'extra_fields': 'long_abstract'})
        result_list = json.loads(response.content)['results']
        for result in result_list:
            self.assertTrue(result.has_key('long_abstract'))


class ApiGetObjectIntegrationTests(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.login()

    def get_object(self, object_type='assets', object_id='A12345', output_format='', query=None,
                                content_type='application/json'):
        if query == None:
            query = {}
        return self.client.get(defines.URL_ROOT + object_type + '/' + object_id + '/' + output_format, 
                query, ACCEPT=content_type)

    def test_get_document_by_id_returns_200(self):
        response = self.get_object(object_type='documents')
        self.assertEqual(200, response.status_code)

    def test_get_object_by_id_returns_200(self):
        response = self.get_object(object_type='objects')
        self.assertEqual(200, response.status_code)

    def test_get_asset_by_id_returns_200(self):
        response = self.get_object()
        self.assertEqual(200, response.status_code)

    def test_extra_fields_with_get_object(self):
        response = self.get_object(object_type='documents', 
                query={'extra_fields': 'long_abstract'})
        result = json.loads(response.content)['results']
        self.assertTrue(result.has_key('long_abstract'))

    def test_404_returned_if_no_object(self):
        response = self.get_object(object_id='A1234567890')
        self.assertEqual(404, response.status_code)

    def test_400_returned_if_unknown_object_type(self):
        response = self.get_object(object_type='foobars')
        self.assertEqual(400, response.status_code)

    def test_400_returned_if_unknown_query_param(self):
        response = self.get_object(object_type='documents', query={'country': 'angola'})
        self.assertEqual(400, response.status_code)

    def test_can_specify_content_type_in_query(self):
        response = self.get_object(query={'_accept': 'application/xml'},
                content_type='text/html')
        self.assertEqual(200, response.status_code)
        self.assertEqual(response['Content-Type'].lower(), 'application/xml')

    def test_extra_fields_with_object_search(self):
        response = self.get_object(object_type='documents', output_format='short',
                query={'extra_fields': 'long_abstract'})
        # not all the results have the abstracts, so just check it doesn't
        # immediately complain
        self.assertEqual(200, response.status_code)


class ApiRootIntegrationTests(BaseTestCase):
    def get_root(self):
        return self.client.get(defines.URL_ROOT, ACCEPT='application/json')

    def test_root_url_returns_200(self):
        response = self.get_root()
        self.assertEqual(200, response.status_code)

    def test_root_url_contains_help_link(self):
        response = self.get_root()
        response_dict = json.loads(response.content)
        self.assertTrue(response_dict['help'].startswith('http://'))

class ApiFieldListIntegrationTests(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def get_field_list(self):
        return self.client.get(defines.URL_ROOT + 'fieldlist/', ACCEPT='application/json')

    def test_field_list_returns_200(self):
        self.login()
        response = self.get_field_list()
        self.assertEqual(200, response.status_code)

    def test_field_list_has_admin_items_for_unlimited_user(self):
        # first check our assumptions
        self.assertTrue('send_email_alerts' in settings.ADMIN_ONLY_FIELDS)
        self.setUserLevel('Unlimited')
        # now run the test
        self.login()
        response = self.get_field_list()
        response_list = json.loads(response.content)
        self.assertTrue(len(response_list) > 1)
        self.assertTrue('send_email_alerts' in response_list)

    def test_field_list_has_no_admin_items_for_partner_user(self):
        # first check our assumptions
        self.assertTrue('send_email_alerts' in settings.ADMIN_ONLY_FIELDS)
        self.assertFalse('asset_publication_date' in settings.GENERAL_FIELDS)
        # now run the test
        self.setUserLevel('Partner')
        self.login()
        response = self.get_field_list()
        response_list = json.loads(response.content)
        self.assertTrue(len(response_list) > 1)
        self.assertFalse('send_email_alerts' in response_list)
        self.assertTrue('asset_publication_date' in response_list)

    def test_field_list_has_no_admin_items_for_general_user(self):
        # first check our assumptions
        self.assertTrue('send_email_alerts' in settings.ADMIN_ONLY_FIELDS)
        self.assertFalse('asset_publication_date' in settings.GENERAL_FIELDS)
        # now run the test
        self.setUserLevel('General User')
        self.login()
        response = self.get_field_list()
        response_list = json.loads(response.content)
        self.assertTrue(len(response_list) > 1)
        self.assertFalse('send_email_alerts' in response_list)
        self.assertFalse('asset_publication_date' in response_list)

class ApiFacetIntegrationTests(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.login()

    def facet_search(self, object_type='assets', facet_type='country', query=None):
        query = query or {'q': 'undp'}
        return self.client.get(defines.URL_ROOT + object_type + '/' + facet_type + '_count/', 
                query, ACCEPT='application/json')

    def test_200_returned_for_all_facet_types(self):
        for facet_type in ('country', 'region', 'keyword', 'sector', 'subject', 'theme'):
            response = self.facet_search(facet_type=facet_type)
            self.assertEqual(200, response.status_code)

    def test_200_returned_for_individual_object_type(self):
        response = self.facet_search(object_type='documents')
        self.assertEqual(200, response.status_code)

    def test_facet_num_results(self):
        response = self.facet_search(query={'q': 'undp', 'num_results': '123'})
        search_results = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(123, len(search_results['country_count']))

    def test_facet_num_results_with_minus_one(self):
        response = self.facet_search(query={'q': 'undp', 'num_results': '-1'})
        search_results = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertTrue(
            len(search_results['country_count']) > 0)

    def test_400_returned_if_unknown_facet_type(self):
        response = self.facet_search(facet_type='foobars')
        self.assertEqual(400, response.status_code)
                
    def test_all_counts_from_facet_gt_0(self):
        response = self.facet_search()
        search_results = json.loads(response.content)
        for country_count in search_results['country_count']:
            self.assertTrue(isinstance(country_count[0], unicode))
            self.assertTrue(isinstance(country_count[1], int))

class ApiCategoryChildrenIntegrationTests(ApiTestsBase):
    def children_search(self, object_type='themes', object_id='C34',
            content_type='application/json'):
        return self.client.get(defines.URL_ROOT + object_type + '/' + object_id + '/children/full', 
                ACCEPT=content_type)
    
    def test_200_returned_for_children_search(self):
        child_searches = {'themes': 'C34', 'itemtypes': 'C1067'} 
        for object_type, object_id in child_searches.items():
            response = self.children_search(object_type=object_type, object_id=object_id)
            self.assertEqual(200, response.status_code)

    def test_parents_match_for_children_search(self):
        response = self.children_search()
        search_results = json.loads(response.content)
        self.assertTrue(0 < int(search_results['metadata']['total_results']))
        for result in search_results['results']:
            self.assertEqual('34', result['cat_parent'])
            
    def test_400_returned_for_asset_child_search(self):
        response = self.children_search(object_type='documents', object_id='A8346')
        self.assertEqual(400, response.status_code)

    def test_400_returned_for_invalid_child(self):
        response = self.children_search(object_type='regions', object_id='C1346')
        self.assertEqual(400, response.status_code)

    def test_all_have_children_link(self):
        for object_type in settings.OBJECT_TYPES_WITH_HIERARCHY:
            response = self.get_all(object_type=object_type, output_format='full') 
            search_results = json.loads(response.content)
            for result in search_results['results']:
                self.assertTrue(result['children_url'].find('children') > -1)
