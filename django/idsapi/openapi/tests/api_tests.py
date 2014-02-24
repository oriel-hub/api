# integration tests at the API level
import json
import re
import datetime

from django.conf import settings
from django.test.testcases import TestCase
from sunburnt import SolrInterface

from openapi import defines
from openapi.search_builder import get_solr_interface
from openapi.tests.test_base import BaseTestCase


class ApiTestsBase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        self.login()

    def object_search(self, site='hub', object_type='documents', output_format='full', query=None,
            content_type='application/json'):
        if query is None:
            query = {'q': 'un'}
        if output_format == 'no_slash':
            output_format = ''
        else:
            output_format = '/' + output_format
        return self.client.get(defines.URL_ROOT + site + '/search/' + object_type + output_format,
                query, ACCEPT=content_type)

    def get_all(self, site='hub', object_type='assets', output_format='', query=None,
            content_type='application/json'):
        if query is None:
            query = {}
        if output_format == 'no_slash':
            output_format = ''
        else:
            output_format = '/' + output_format
        return self.client.get(defines.URL_ROOT + site + '/get_all/' + object_type + output_format,
                query, ACCEPT=content_type)

    def assert_non_zero_result_len(self, response, element='results'):
        search_results = json.loads(response.content)[element]
        self.assertTrue(len(search_results) > 0, "Expected more than zero search results")
        return search_results

    def assert_results_list(self, response, pass_test, element='results', msg=None):
        for result in self.assert_non_zero_result_len(response, element):
            self.assertTrue(pass_test(result), msg)

    def assert_results_list_if_present(self, response, required_field, pass_test, element='results', msg=None):
        self.assertStatusCode(response)
        for result in self.assert_non_zero_result_len(response, element):
            if required_field in result:
                self.assertTrue(pass_test(result[required_field]), msg)

    def assertStatusCode(self, response, status_code=200):
        self.assertEqual(status_code, response.status_code, response.content)

    def assert_metadata_solr_query_included_when_admin_fields_is_false(self, returns_response):
        self.setUserLevel('Unlimited')
        self.login()
        test_user_level = self.user.get_profile().user_level
        self.assertFalse(settings.USER_LEVEL_INFO[test_user_level]['hide_admin_fields'],
            "We expect hide_admin_fields to be False.")

        response = returns_response(self)
        response_list = json.loads(response.content)
        self.assertTrue('solr_query' in response_list['metadata'])

    def assert_metadata_solr_query_not_included_when_admin_fields_is_true(self, returns_response):
        self.setUserLevel('General User')
        self.login()
        test_user_level = self.user.get_profile().user_level
        self.assertTrue(settings.USER_LEVEL_INFO[test_user_level]['hide_admin_fields'],
            "We expect hide_admin_fields to be False.")

        response = returns_response(self)
        response_list = json.loads(response.content)
        self.assertFalse('solr_query' in response_list['metadata'])


class ApiSearchResponseTests(ApiTestsBase):

    def test_id_only_search_returns_200(self):
        response = self.object_search(output_format='id')
        self.assertStatusCode(response)

    def test_json_id_only_search_returns_only_ids(self):
        response = self.object_search(output_format='id')
        self.assert_results_list(response, lambda x: sorted(x.keys()) == ['item_id', 'metadata_url'])

    def test_search_works_without_trailing_slash(self):
        response = self.object_search(output_format='no_slash')
        self.assertStatusCode(response)

    def test_json_short_search_returns_short_fields(self):
        response = self.object_search(output_format='short')
        self.assert_results_list(response, lambda x: sorted(x.keys()) == ['item_id', 'item_type', 'metadata_url', 'title'])

    def test_json_full_search_returns_more_than_3_fields(self):
        response = self.object_search(output_format='full')
        self.assert_results_list(response, lambda x: len(x.keys()) > 3, msg="Full search should have more than 3 fields")

    def test_json_full_search_does_not_contain_facet_fields(self):
        response = self.object_search(output_format='full')
        self.assert_results_list(response, lambda x: all(not key.endswith('_facet') for key in x.keys()), msg="Full search should not show facet fields")

    def test_json_full_search_does_not_contain_hidden_fields(self):
        response = self.object_search(output_format='full')
        self.assert_results_list(response,
                lambda x: all(key not in settings.ADMIN_ONLY_FIELDS for key in x.keys()),
                msg="Full search should not show hidden fields")

    def test_can_specify_content_type_in_query(self):
        response = self.object_search(query={'q': 'un', '_accept': 'application/json'},
                content_type='text/html')
        self.assertStatusCode(response)
        self.assertEqual(response['Content-Type'].lower(), 'application/json')

    def test_assets_search_contains_only_assets(self):
        response = self.object_search(output_format='short',
                query={'q': 'Agricultural', 'num_results': '500'})
        self.assert_results_list(response,
                lambda x: x['object_type'] in defines.ASSET_NAMES,
                msg="Search should have only asset objects")

    def test_description_contains_image_beacon(self):
        response = self.object_search(object_type='documents', output_format='full')
        profile = self.user.get_profile()

        def check_image_beacon_exists_and_has_correct_id(description):
            return ((description.find(settings.IMAGE_BEACON_STUB_URL) > -1) and
                    (description.find(profile.beacon_guid) > -1))
        self.assert_results_list_if_present(response, 'description', check_image_beacon_exists_and_has_correct_id)

    def test_description_does_not_contain_image_beacon_for_unlimited_user(self):
        self.setUserLevel('Unlimited')
        response = self.object_search(object_type='documents', output_format='full')
        self.assert_results_list_if_present(response, 'description', lambda x: x.find(settings.IMAGE_BEACON_STUB_URL) == -1)

    def test_full_search_converts_structured_xml_fields(self):
        response = self.object_search(object_type='documents', output_format='full')
        self.assert_results_list_if_present(response, 'category_theme_array', lambda x: isinstance(x["theme"], list))

    def test_short_search_converts_structured_xml_fields(self):
        response = self.object_search(object_type='documents', output_format='short',
                query={'q': 'un', 'extra_fields': 'category_theme_array'})
        self.assert_results_list_if_present(response, 'category_theme_array', lambda x: isinstance(x["theme"], list))


class ApiSearchIntegrationTests(ApiTestsBase):

    def test_query_by_country(self):
        response = self.object_search(query={'country': 'Namibia|NA'})
        self.assert_results_list(response, lambda x: ' '.join(x['country_focus']).lower().find('namibia') > -1)

    def test_query_by_country_and_free_text(self):
        response = self.object_search(query={'q': 'un', 'country': 'angola'})
        self.assertStatusCode(response)

    def test_query_by_each_query_term(self):
        query_term_list = [
                {'country': 'A1100|country|India|IN'},
                {'keyword': 'agriculture'},
                {'region': 'C21|region|Africa'},
                {'sector': 'agriculture'},
                #{'subject': 'gdn'},                # TODO: Why is this commented out?
                {'theme': 'C531|theme|Governance'},
        ]
        for query_term in query_term_list:
            response = self.object_search(query=query_term)
            self.assertStatusCode(response)
            search_results = json.loads(response.content)
            self.assertTrue(search_results['metadata']['total_results'] > 0)

    def test_query_using_bridge(self):
        response = self.object_search(site='bridge')
        self.assertStatusCode(response)
        # TODO: reinstate when bridge is sorted out
        #search_results = json.loads(response.content)
        #self.assertTrue(search_results['metadata']['total_results'] > 0)

    def test_query_by_boolean_country_and_free_text(self):
        response = self.object_search(query={'q': 'un', 'country': 'angola&tanzania'})
        self.assertStatusCode(response)

    def test_query_by_country_with_and(self):
        response = self.object_search(query={'country': 'angola&namibia'})
        self.assert_results_list_if_present(
            response, 'country_focus', lambda x: 'Angola' in x and 'Namibia' in x)

    def test_query_by_country_with_or(self):
        response = self.object_search(query={'country': 'namibia|iran'})
        self.assert_results_list_if_present(
            response, 'country_focus', lambda x: 'Iran' in x or 'Namibia' in x)

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
            # should now have something like ['hub', 'get', 'documents', '1234', 'full', 'asdf']
            self.assertEqual(len(url_bits), 6)
            self.assertEqual(url_bits[0], 'hub')
            self.assertEqual(url_bits[1], 'get')
            self.assertNotEqual(url_bits[2], 'assets')
            self.assertTrue(url_bits[2] in defines.OBJECT_TYPES)
            self.assertTrue(re.match(r'^[AC]\d+$', url_bits[3]) is not None)
            self.assertEqual(url_bits[4], 'full')
            self.assertTrue(re.match(r'^[-\w]+$', url_bits[5]) is not None)
            self.assertFalse(url_bits[5].startswith('-'))
            self.assertFalse(url_bits[5].endswith('-'))

    def test_document_search_returns_200(self):
        response = self.object_search(object_type='documents')
        self.assertStatusCode(response)

    def test_all_document_search_returns_400(self):
        response = self.object_search(query={'all': ''})
        self.assertStatusCode(response, 400)

    def test_200_returned_if_no_results(self):
        response = self.object_search(query={'country': 'NoddyLand'})
        self.assertStatusCode(response)
        # this test is just to check the search actually returned zero results
        search_results = json.loads(response.content)
        self.assertEqual(0, search_results['metadata']['total_results'])
        self.assertEqual(0, len(search_results['results']))

    def test_200_returned_for_trailing_star(self):
        response = self.object_search(query={'keyword': 'af*'})
        self.assertStatusCode(response)

    def test_200_returned_for_middle_star(self):
        response = self.object_search(query={'keyword': 'af*ca'})
        self.assertStatusCode(response)

    def test_document_specific_query_param_author(self):
        response = self.object_search(object_type='documents', query={'author': 'john'})
        self.assertStatusCode(response)
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertTrue(' '.join(result['author']).lower().find('john') > -1)

    def test_organisation_specific_query_param_acronym(self):
        response = self.object_search(object_type='organisations', query={'acronym': 'UNDP'})
        self.assertStatusCode(response)
        self.assertTrue(0 < json.loads(response.content)['metadata']['total_results'])
        search_results = json.loads(response.content)['results']
        for result in search_results:
            acronym_found = result['acronym'].lower().find('un') > -1
            alternative_acronym_found = False
            if 'alternative_acronym' in result:
                alternative_acronym_found = ' '.join(result['alternative_acronym']).lower().find('un') > -1
            self.assertTrue(acronym_found or alternative_acronym_found)

    def test_item_specific_query_param_item_type(self):
        # need to be unlimited to see the item_type
        self.setUserLevel('Unlimited')
        response = self.object_search(object_type='items', query={'item_type': 'Jobs'})
        self.assertStatusCode(response)
        self.assertTrue(0 < json.loads(response.content)['metadata']['total_results'])
        search_results = json.loads(response.content)['results']
        for result in search_results:
            self.assertEqual('Jobs', result['item_type'])

    def test_num_results_only_returns_only_total_results(self):
        response = self.object_search(query={'q': 'un', 'num_results_only': None})
        self.assertStatusCode(response)
        response_dict = json.loads(response.content)
        self.assertIn('metadata', response_dict)
        self.assertNotIn('results', response_dict)
        self.assertEqual(1, len(response_dict['metadata'].keys()))
        self.assertIn('total_results', response_dict['metadata'])

    def test_extra_fields_with_object_search(self):
        response = self.object_search(object_type='documents', output_format='short',
                query={'q': 'un', 'extra_fields': 'description'})
        # not all the results have the abstracts, so just check it doesn't
        # immediately complain
        self.assertStatusCode(response)

    def test_search_is_case_insensitive(self):
        response_upper = self.object_search(object_type='documents', query={'q': 'AGRI*'})
        response_upper_data = json.loads(response_upper.content)
        response_lower = self.object_search(object_type='documents', query={'q': 'agri*'})
        response_lower_data = json.loads(response_lower.content)
        self.assertEqual(response_upper_data['metadata']['total_results'],
                response_lower_data['metadata']['total_results'])

    def test_search_has_default_site_hub(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'un', 'num_results': '500'})
        results = json.loads(response.content)['results']
        for result in results:
            self.assertEqual('hub', result['site'])

    def test_metadata_solr_query_depends_on_hide_admin_field_value(self):
        returns_response = lambda x: x.object_search()
        self.assert_metadata_solr_query_included_when_admin_fields_is_false(returns_response)
        self.assert_metadata_solr_query_not_included_when_admin_fields_is_true(returns_response)


class ApiPaginationTests(ApiTestsBase):

    def test_search_response_has_metadata(self):
        response = self.object_search()
        metadata = json.loads(response.content)['metadata']
        self.assertIn('total_results', metadata)
        self.assertIn('start_offset', metadata)

    def test_search_response_has_next_in_metadata(self):
        response = self.object_search()
        metadata = json.loads(response.content)['metadata']
        self.assertIn('next_page', metadata)
        self.assertTrue(metadata['next_page'].find('num_results') > -1)
        self.assertTrue(metadata['next_page'].find('start_offset') > -1)
        # also, default search should not have prev_page link
        self.assertNotIn('prev_page', metadata)

    def test_2nd_page_has_prev_in_metadata(self):
        response = self.object_search(query={'q': 'un', 'start_offset': '10'})
        metadata = json.loads(response.content)['metadata']
        self.assertIn('prev_page', metadata)
        self.assertTrue(metadata['prev_page'].find('num_results') > -1)
        self.assertTrue(metadata['prev_page'].find('start_offset') > -1)

    def test_prev_never_has_negative_start_offset(self):
        response = self.object_search(query={'q': 'un', 'start_offset': '1'})
        metadata = json.loads(response.content)['metadata']
        self.assertIn('prev_page', metadata)
        match = re.search(r'start_offset=([-0-9]+)', metadata['prev_page'])
        self.assertTrue(int(match.group(1)) >= 0)

    def test_num_results_in_query_matches_results_returned(self):
        response = self.object_search(query={'q': 'un', 'num_results': '20'})
        results = json.loads(response.content)['results']
        self.assertEqual(20, len(results))

    def test_num_results_correctly_passed_on_to_next_and_prev_links(self):
        response = self.object_search(object_type='documents',
                query={'q': 'un', 'num_results': '12', 'start_offset': '12'})
        metadata = json.loads(response.content)['metadata']
        for link in ('prev_page', 'next_page'):
            match = re.search(r'num_results=([-0-9]+)', metadata[link])
            self.assertTrue(int(match.group(1)) == 12)


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
        def published_after_query_date(publication_date):
            query_date = datetime.datetime.strptime('2002-6-1', "%Y-%m-%d")
            document_published = datetime.datetime.strptime(
                    publication_date[0:19], "%Y-%m-%d %H:%M:%S")
            return document_published >= query_date

        response = self.object_search(query={'document_published_after': '2002-06-01'})
        self.assert_results_list_if_present(response, 'publication_date', published_after_query_date)

    def test_200_returned_for_document_published_year(self):
        def published_in_2002(publication_date):
            document_published = datetime.datetime.strptime(publication_date[0:19], "%Y-%m-%d %H:%M:%S")
            return document_published.year == 2002

        response = self.object_search(query={'document_published_year': '2002'})
        self.assert_results_list_if_present(response, 'publication_date', published_in_2002)

    def test_200_returned_for_item_dates(self):
        for query_param in ['item_started_after', 'item_started_before', 'item_finished_after',
                'item_finished_before']:
            response = self.object_search(query={query_param: '2008-12-31'})
            self.assertStatusCode(response)

    def test_200_returned_for_item_years(self):
        for query_param in ['item_started_year', 'item_finished_year']:
            response = self.object_search(query={query_param: '2008'})
            self.assertStatusCode(response)

    def test_400_returned_for_document_published_before_bad_date_format(self):
        bad_dates = ['200-12-31', '2008-1-01', '2008-01-1', '20080101', '200A-01-01']
        for date in bad_dates:
            response = self.object_search(object_type='documents', query={'document_published_before': date})
            self.assertStatusCode(response, 400)

    def test_400_returned_for_document_published_year_bad_date_format(self):
        bad_dates = ['200', '200A', '20080']
        for date in bad_dates:
            response = self.object_search(object_type='documents', query={'document_published_year': date})
            self.assertStatusCode(response, 400)


class ApiSearchSortTests(ApiTestsBase):

    def test_sort_ascending_by_publication_date(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'un', 'sort_asc': 'publication_date'})
        results = json.loads(response.content)['results']
        self.assertTrue(len(results) >= 5)
        for i in range(len(results) - 1):
            date1 = datetime.datetime.strptime(results[i]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            date2 = datetime.datetime.strptime(results[i + 1]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(date1 <= date2)

    def test_sort_descending_by_publication_date(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'un', 'sort_desc': 'publication_date'})
        results = json.loads(response.content)['results']
        self.assertTrue(len(results) >= 5)
        for i in range(len(results) - 1):
            date1 = datetime.datetime.strptime(results[i]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            date2 = datetime.datetime.strptime(results[i + 1]['publication_date'][0:19], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(date1 >= date2)

    def test_400_returned_for_disallowed_sort_field(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'un', 'sort_asc': 'description'})
        self.assertStatusCode(response, 400)

    def test_400_returned_for_unknown_sort_field(self):
        response = self.object_search(object_type='documents', output_format='full',
                query={'q': 'un', 'sort_desc': 'foobar'})
        self.assertStatusCode(response, 400)


class ApiSearchErrorTests(ApiTestsBase):

    def test_400_returned_if_no_q_parameter(self):
        response = self.object_search(query={})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_unknown_site(self):
        response = self.object_search(site="no_site")
        self.assertStatusCode(response, 400)

    def test_400_returned_if_unknown_object_type(self):
        response = self.object_search(object_type='foobars')
        self.assertStatusCode(response, 400)

    def test_400_returned_if_unknown_output_format(self):
        response = self.object_search(output_format='foobar')
        self.assertStatusCode(response, 400)

    def test_400_returned_if_unknown_query_parameter(self):
        response = self.object_search(query={'foo': 'bar'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_query_parameter_has_no_value(self):
        response = self.object_search(query={'country': ''})
        self.assertStatusCode(response, 400)

    def test_404_returned_for_unknown_path(self):
        response = self.client.get('/openapi/foobar')
        self.assertStatusCode(response, 404)

    # TODO: fails - framework bug? think about this ...
    #def test_406_returned_if_unknown_return_format(self):
    #    response = self.object_search(content_type='application/foobar')
    #    self.assertStatusCode(response, 406)

    def test_405_returned_for_post_method_not_allowed(self):
        response = self.client.post(defines.URL_ROOT + 'hub/search/documents',
                {'q': 'un'}, ACCEPT='application/json')
        self.assertStatusCode(response, 405)

    def test_400_returned_for_repeated_country_search(self):
        response = self.object_search(query={'country': ['namibia', 'angola']})
        self.assertContains(response, 'country', status_code=400)

    def test_query_by_country_with_both_or_and_and(self):
        response = self.object_search(query={'country': 'angola|iran&namibia'})
        self.assertStatusCode(response, 400)

    def test_400_returned_for_leading_star(self):
        response = self.object_search(query={'keyword': '*ca'})
        self.assertStatusCode(response, 400)

    def test_400_returned_for_bad_date_query_param_prefix(self):
        response = self.object_search(query={'foobar_published_year': '2009'})
        self.assertStatusCode(response, 400)

    def test_400_returned_for_bad_date_query_param_postfix(self):
        response = self.object_search(object_type='documents', query={'document_published_foobar': '2009'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_document_specific_query_param_used(self):
        response = self.object_search(object_type='assets', query={'author': 'John'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_num_results_is_negative(self):
        response = self.object_search(query={'q': 'un', 'num_results': '-1'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_start_offset_is_negative(self):
        response = self.object_search(query={'q': 'un', 'start_offset': '-1'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_num_results_is_non_numeric(self):
        response = self.object_search(query={'q': 'un', 'num_results': 'not_a_number'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_start_offset_is_non_numeric(self):
        response = self.object_search(query={'q': 'un', 'start_offset': 'not_a_number'})
        self.assertStatusCode(response, 400)

    def test_400_returned_if_sort_asc_and_sort_desc_used(self):
        response = self.object_search(query={
            'q': 'un',
            'sort_asc': 'publication_date',
            'sort_desc': 'object_id'
        })
        self.assertStatusCode(response, 400)


class GetSolrInterfaceTests(TestCase):

    def test_get_solr_interface_returns_same_object_normally(self):
        si1 = get_solr_interface('hub')
        si2 = get_solr_interface('hub')
        self.assertIs(si1, si2)
        self.assertIsInstance(si1, SolrInterface)

    def test_get_solr_interface_returns_different_object_for_different_sites(self):
        si1 = get_solr_interface('hub')
        si2 = get_solr_interface('bridge')
        self.assertIsNot(si1, si2)
        self.assertIsInstance(si1, SolrInterface)
        self.assertIsInstance(si2, SolrInterface)

    def test_get_solr_interface_returns_different_object_if_global_is_blanked(self):
        si1 = get_solr_interface('hub')
        from .. import search_builder
        del search_builder.saved_solr_interface['hub']
        si2 = get_solr_interface('hub')
        self.assertIsNot(si1, si2)
        self.assertIsInstance(si1, SolrInterface)
        self.assertIsInstance(si2, SolrInterface)

    def test_get_solr_interface_returns_different_object_if_time_reset(self):
        si1 = get_solr_interface('hub')
        from .. import search_builder
        search_builder.solr_interface_created['hub'] = datetime.datetime(2000, 1, 1)
        si2 = get_solr_interface('hub')
        self.assertIsNot(si1, si2)
        self.assertIsInstance(si1, SolrInterface)
        self.assertIsInstance(si2, SolrInterface)


class ApiGetAllIntegrationTests(ApiTestsBase):

    def test_get_all_documents_returns_200(self):
        response = self.get_all(object_type='documents')
        self.assertStatusCode(response)

    def test_get_all_documents_returns_200_no_trailing_slash(self):
        response = self.get_all(object_type='documents', output_format='no_slash')
        self.assertStatusCode(response)

    def test_get_all_bridge_documents_returns_200(self):
        response = self.get_all(site="bridge", object_type='documents')
        self.assertStatusCode(response)

    def test_get_all_assets_returns_200(self):
        response = self.get_all()
        self.assertStatusCode(response)

    def test_400_returned_if_unknown_object_type(self):
        response = self.get_all(object_type='foobars')
        self.assertStatusCode(response, 400)

    def test_extra_fields_with_all_assets(self):
        response = self.get_all(object_type='documents',
                query={'extra_fields': 'description'})
        result_list = json.loads(response.content)['results']
        for result in result_list:
            self.assertTrue('description' in result)


class ApiGetObjectIntegrationTests(ApiTestsBase):

    def get_object(self, site='hub', object_type='documents', item_id='A66345',
            output_format='', query=None, content_type='application/json'):
        if not query:
            query = {}
        if output_format == 'no_slash':
            output_format = ''
        else:
            output_format = '/' + output_format
        return self.client.get(defines.URL_ROOT + site + '/get/' + object_type
                + '/' + item_id + output_format, query, ACCEPT=content_type)

    def test_get_document_by_id_returns_200(self):
        response = self.get_object(object_type='documents')
        self.assertStatusCode(response)

    def test_get_document_by_id_no_trailing_slash_returns_200(self):
        response = self.get_object(object_type='documents',
                output_format='no_slash')
        self.assertStatusCode(response)

# TODO: reinstate when bridge is sorted out
#    def test_bridge_get_document_by_id_returns_200(self):
#        response = self.get_object(site='bridge', object_type='documents',
#                item_id='A20922')
#       self.assertStatusCode(response)

    def test_get_object_by_id_returns_200(self):
        response = self.get_object(object_type='objects')
        self.assertStatusCode(response)

    def test_get_asset_by_id_returns_200(self):
        response = self.get_object()
        self.assertStatusCode(response)

    def test_extra_fields_with_get_object(self):
        response = self.get_object(object_type='documents',
                query={'extra_fields': 'description'})
        result = json.loads(response.content)['results']
        self.assertTrue('description' in result)

    def test_404_returned_if_no_object(self):
        response = self.get_object(item_id='A1234567890')
        self.assertStatusCode(response, 404)

    def test_400_returned_if_unknown_object_type(self):
        response = self.get_object(object_type='foobars')
        self.assertStatusCode(response, 400)

    def test_400_returned_if_unknown_query_param(self):
        response = self.get_object(object_type='documents', query={'country': 'angola'})
        self.assertStatusCode(response, 400)

    def test_get_object_by_id_with_xml_returns_200(self):
        response = self.get_object(object_type='objects', content_type=None,
                                   query={'format': 'xml'})
        self.assertStatusCode(response)

    def test_can_specify_content_type_in_query(self):
        response = self.get_object(query={'_accept': 'application/xml'},
                content_type='text/html')
        self.assertStatusCode(response)
        self.assertEqual(response['Content-Type'].lower(), 'application/xml')

    def test_extra_fields_with_object_search(self):
        response = self.get_object(object_type='documents', output_format='short',
                query={'extra_fields': 'description'})
        # not all the results have the abstracts, so just check it doesn't
        # immediately complain
        self.assertStatusCode(response)

    def test_invalid_extra_field_in_object_search_returns_api_error(self):
        response = self.get_object(object_type='documents', output_format='short',
                query={'extra_fields': 'not_a_valid_field'})
        self.assertStatusCode(response, 400)
        expected_message = '"Invalid query: Can\'t limit Fields - Fields not defined in schema: [u\'not_a_valid_field\']"'
        self.assertEquals(response.content, expected_message)


class ApiRootIntegrationTests(ApiTestsBase):
    def get_root(self):
        return self.client.get(defines.URL_ROOT, ACCEPT='application/json')

    def test_root_url_returns_200(self):
        response = self.get_root()
        self.assertStatusCode(response)

    def test_root_url_contains_help_link(self):
        response = self.get_root()
        response_dict = json.loads(response.content)
        self.assertTrue(response_dict['help'].startswith('http://'))


class ApiFieldListIntegrationTests(ApiTestsBase):
    def get_field_list(self, site='hub'):
        return self.client.get(defines.URL_ROOT + site + '/fieldlist/', ACCEPT='application/json')

    def test_field_list_returns_200(self):
        self.login()
        response = self.get_field_list()
        self.assertStatusCode(response)

    def test_bridge_field_list_returns_200(self):
        self.login()
        response = self.get_field_list(site='bridge')
        self.assertStatusCode(response)

    def test_bad_site_field_list_returns_400(self):
        self.login()
        response = self.get_field_list(site='no_such_site')
        self.assertStatusCode(response, 400)

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


class ApiFacetIntegrationTests(ApiTestsBase):

    def facet_search(self, site='hub', object_type='documents', facet_type='country', query=None):
        query = query or {'q': 'un'}
        return self.client.get(defines.URL_ROOT + site + '/count/' + object_type + '/' + facet_type,
                query, ACCEPT='application/json')

    def test_200_returned_for_all_facet_types(self):
        for facet_type in ('country', 'region', 'keyword', 'sector', 'subject', 'theme'):
            response = self.facet_search(facet_type=facet_type)
            self.assertStatusCode(response)

    def test_200_returned_for_individual_object_type(self):
        response = self.facet_search(object_type='documents')
        self.assertStatusCode(response)

    def test_facet_num_results(self):
        num_results = 12
        response = self.facet_search(query={'q': 'un', 'num_results': str(num_results)})
        search_results = json.loads(response.content)
        self.assertStatusCode(response)
        self.assertEqual(num_results, len(search_results['country_count']))

    def test_facet_num_results_with_minus_one(self):
        response = self.facet_search(query={'q': 'un', 'num_results': '-1'})
        search_results = json.loads(response.content)
        self.assertStatusCode(response)
        self.assertTrue(len(search_results['country_count']) > 0)

    def test_400_returned_if_unknown_facet_type(self):
        response = self.facet_search(facet_type='foobars')
        self.assertStatusCode(response, 400)

    def test_all_facets_have_an_integer_count(self):
        response = self.facet_search()

        def check_all_facets_have_an_integer_count(country_count):
            return ('item_id' in country_count and 'metadata_url' in country_count and
                    isinstance(country_count['count'], int))
        self.assert_results_list(response, check_all_facets_have_an_integer_count,
                element='country_count')

    def test_facets_with_zero_count_excluded_by_setting(self):
        old_setting = settings.EXCLUDE_ZERO_COUNT_FACETS
        try:
            settings.EXCLUDE_ZERO_COUNT_FACETS = True
            response = self.facet_search()
            self.assert_results_list(response, lambda x: x['count'] > 0,
                    element='country_count')
        finally:
            settings.EXCLUDE_ZERO_COUNT_FACETS = old_setting

    def test_facets_with_zero_count_included_by_setting(self):
        old_setting = settings.EXCLUDE_ZERO_COUNT_FACETS
        try:
            settings.EXCLUDE_ZERO_COUNT_FACETS = False
            response = self.facet_search()
            zero_found = False
            for result in self.assert_non_zero_result_len(response, element='country_count'):
                if result['count'] == 0:
                    zero_found = True
            self.assertTrue(zero_found, "Did not find any results with a zero count")
        finally:
            settings.EXCLUDE_ZERO_COUNT_FACETS = old_setting

    def test_metadata_solr_query_depends_on_hide_admin_field_value(self):
        returns_response = lambda x: x.facet_search()
        self.assert_metadata_solr_query_included_when_admin_fields_is_false(returns_response)
        self.assert_metadata_solr_query_not_included_when_admin_fields_is_true(returns_response)


class ApiCategoryChildrenIntegrationTests(ApiTestsBase):
    def children_search(self, site='hub', object_type='themes', item_id='34',
            content_type='application/json'):
        return self.client.get(defines.URL_ROOT + site + '/get_children/' +
                object_type + '/' + item_id + '/full', ACCEPT=content_type)

    def test_200_returned_for_children_search(self):
        child_searches = {'themes': '34', 'itemtypes': '1067'}
        for object_type, item_id in child_searches.items():
            response = self.children_search(object_type=object_type, item_id=item_id)
            self.assertStatusCode(response)

    def test_parents_match_for_children_search(self):
        response = self.children_search()
        search_results = json.loads(response.content)
        self.assertTrue(0 < int(search_results['metadata']['total_results']))
        for result in search_results['results']:
            self.assertEqual('34', result['cat_parent'])

    def test_400_returned_for_asset_child_search(self):
        response = self.children_search(object_type='documents', item_id='A8346')
        self.assertStatusCode(response, 400)

    def test_400_returned_for_invalid_child(self):
        response = self.children_search(object_type='regions', item_id='1346')
        self.assertStatusCode(response, 400)

    def test_all_have_children_link(self):
        for object_type in settings.OBJECT_TYPES_WITH_HIERARCHY:
            response = self.get_all(object_type=object_type, output_format='full')
            search_results = json.loads(response.content)
            for result in search_results['results']:
                self.assertTrue(result['children_url'].find('children') > -1)

    def test_metadata_solr_query_depends_on_hide_admin_field_value(self):
        returns_response = lambda x: x.children_search(object_type='themes', item_id='34')
        self.assert_metadata_solr_query_included_when_admin_fields_is_false(returns_response)
        self.assert_metadata_solr_query_not_included_when_admin_fields_is_true(returns_response)
