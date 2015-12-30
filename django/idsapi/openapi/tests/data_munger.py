# tests for the data munger
import copy

from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.test.utils import override_settings

from ..search_builder import SearchParams, InvalidOutputFormat
from ..data import (
    DataMunger, SourceLangParser, ObjectDataFilter, MetaDataURLCreator
)

PREFER_TEST_DICT = {
    "title": {
        "bridge": {
            "en": "title goes here",
            "fr": "le title est ici"
        },
        "eldis": {
            "en": "the title goes here"
        }
    }
}


class DataMungerTests(TestCase):

    def setUp(self):
        self.data = DataMunger('hub', SearchParams({}))
        self.data.metadata = MetaDataURLCreator('Document', '789', 'hub')

    def assert_endswith(self, full_string, expected_end):
        self.assertTrue(full_string.endswith(expected_end),
                        'Got: %s\nExpected end: %s' % (full_string, expected_end))

    def test_convert_facet_string(self):
        test_string = "1200|Country|South Africa"
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], '1200')
        self.assertEquals(facet_dict['object_type'], 'Country')
        self.assertEquals(facet_dict['object_name'], 'South Africa')
        self.assert_endswith(facet_dict['metadata_url'],
                             '/v1/hub/get/countries/1200/full/south-africa/')

    def test_convert_facet_string_with_xml_field(self):
        test_string = "<theme><object_id>563</object_id><object_type>Theme</object_type><object_name>Health Challenges</object_name><level>1</level></theme>"
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], '563')
        self.assertEquals(facet_dict['object_type'], 'Theme')
        self.assertEquals(facet_dict['object_name'], 'Health Challenges')
        self.assertEquals(facet_dict['level'], '1')
        self.assert_endswith(facet_dict['metadata_url'],
                             '/v1/hub/get/themes/563/full/health-challenges/')

    def test_convert_xml_string_with_single_string_produces_dict_and_metadata_url(self):
        test_string = "<languageList><Language><title>10 big ideas</title><isocode>en</isocode><description><p>This report argues that blah</p></description><language_id>1</language_id></Language></languageList>"
        theme_data = self.data._convert_xml_field(test_string)
        self.assertEquals(theme_data['Language'][0]['title'], '10 big ideas')
        self.assertEquals(theme_data['Language'][0]['language_id'], '1')
        self.assertEquals(theme_data['Language'][0]['isocode'], 'en')

    def test_convert_xml_string_with_list_of_strings(self):
        test_list = [
            "<list-item><subject><object_id>C1842</object_id><object_type>subject</object_type><object_name>Funder</object_name><level>1</level></subject></list-item>",
            "<list-item><subject><object_id>C1901</object_id><object_type>subject</object_type><object_name>Source</object_name><level>1</level></subject></list-item>",
        ]
        theme_data = self.data._convert_xml_field(test_list)
        self.assertEquals(theme_data[0]['subject']['object_id'], 'C1842')
        self.assertEquals(theme_data[1]['subject']['object_name'], 'Source')

    def test_convert_empty_facet_string_returns_dict_with_empty_values(self):
        test_string = ""
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], '')
        self.assertEquals(facet_dict['object_type'], '')
        self.assertEquals(facet_dict['object_name'], '')
        self.assertEquals(facet_dict['metadata_url'], '')

    def test_convert_old_style_facet_string_returns_dict_with_just_object_name(self):
        test_string = "environmental statistics"
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], '')
        self.assertEquals(facet_dict['object_type'], '')
        self.assertEquals(facet_dict['object_name'], 'environmental statistics')
        self.assertEquals(facet_dict['metadata_url'], '')


class SourceLangParserTests(TestCase):

    def setUp(self):
        self.slp = SourceLangParser(SearchParams({}))

    def test_create_source_lang_dict_works(self):
        result = {
            "object_id_hub_zz": 1234,
            "object_id_eldis_zz": 'A2345',
            "et_al_bridge_zz": "some people",
            "et_al_eldis_zz": "similar people",
            "keyword_eldis_en": ["research", "tfmimport"],
            "keyword_facet_hub_zx": ["research", "tfmimport"],
            "keyword_search_hub_zx": ["research", "tfmimport"],
            "title_bridge_en": "title goes here",
            "title_bridge_fr": "le title est ici",
            "title_eldis_en": "the title goes here",
            "title_search_hub_zx": ["title goes here", "le title est ici"],
            "title_sort_hub_en": "title goes here",
        }
        expected_dict = {
            "object_id": {
                'hub': 1234,
                'eldis': 'A2345',
            },
            "et_al": {
                "bridge": "some people",
                "eldis": "similar people"
            },
            "keyword": {
                "eldis": {
                    "en": ["research", "tfmimport"],
                }
            },
            "title": {
                "bridge": {
                    "en": "title goes here",
                    "fr": "le title est ici"
                },
                "eldis": {
                    "en": "the title goes here"
                }
            }
        }
        with override_settings(GENERIC_FIELD_LIST=['object_id']):
            actual_dict = self.slp.create_source_lang_dict(result)
        self.assertDictEqual(expected_dict, actual_dict)

    def test_field_type_prefix_with_field_name_with_no_underscore(self):
        prefix, source, lang = self.slp.field_type_prefix('content')
        self.assertEqual('content', prefix)
        self.assertIsNone(source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_id_field(self):
        prefix, source, lang = self.slp.field_type_prefix('object_id')
        self.assertEqual('object_id', prefix)
        self.assertIsNone(source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_field_in_generic_field_list_setting(self):
        with override_settings(GENERIC_FIELD_LIST=['metadata_languages']):
            prefix, source, lang = self.slp.field_type_prefix('metadata_languages')
        self.assertEqual('metadata_languages', prefix)
        self.assertIsNone(source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_source_but_no_language(self):
        prefix, source, lang = self.slp.field_type_prefix('et_al_eldis_zz')
        self.assertEqual('et_al', prefix)
        self.assertEqual('eldis', source)
        self.assertEqual('zz', lang)

    def test_field_type_prefix_with_field_name_with_source_and_language(self):
        prefix, source, lang = self.slp.field_type_prefix('title_eldis_en')
        self.assertEqual('title', prefix)
        self.assertEqual('eldis', source)
        self.assertEqual('en', lang)

    def test_exclude_field_ignores_search_api_fields(self):
        # there are all actual fields from the data
        self.assertTrue(self.slp.exclude_field('sm_search_api_source_hub_zz'))
        self.assertTrue(self.slp.exclude_field('dm_search_api_date_updated_hub_zz'))
        self.assertTrue(self.slp.exclude_field('ss_search_api_language'))
        self.assertTrue(self.slp.exclude_field('ss_search_api_type_hub_un'))

    def test_exclude_field_does_not_ignore_search_api_fields_with_more_than_2_letter_prefix(self):
        self.assertFalse(self.slp.exclude_field('another_search_api_source_hub_zz'))

    def test_exclude_field_ignores_hub_search_sort_and_facet_fields(self):
        self.assertTrue(self.slp.exclude_field('title_sort_hub_en'))
        self.assertTrue(self.slp.exclude_field('title_search_hub_zx'))
        self.assertTrue(self.slp.exclude_field('country_focus_facet_hub_zz'))

    def test_exclude_field_does_not_ignore_other_fields(self):
        self.assertFalse(self.slp.exclude_field('title_hub_en'))
        self.assertFalse(self.slp.exclude_field('object_id_eldis_zz'))

    def test_exclude_lang_includes_lang_if_lang_only_not_set(self):
        self.slp.search_params = SearchParams({})
        self.assertFalse(self.slp.exclude_lang('en'))

    def test_exclude_lang_includes_lang_if_lang_only_is_same(self):
        self.slp.search_params = SearchParams({'lang_only': 'en'})
        self.assertFalse(self.slp.exclude_lang('en'))

    def test_exclude_lang_excludes_lang_if_lang_only_is_different(self):
        self.slp.search_params = SearchParams({'lang_only': 'es'})
        self.assertTrue(self.slp.exclude_lang('en'))

    def test_exclude_lang_excludes_lang_if_lang_is_zx(self):
        self.slp.search_params = SearchParams({})
        self.assertTrue(self.slp.exclude_lang('zx'))

    def test_exclude_lang_includes_lang_if_lang_is_zz(self):
        self.slp.search_params = SearchParams({})
        self.assertFalse(self.slp.exclude_lang('zz'))

    def test_prefer_lang_does_not_modify_out_dict_if_lang_pref_not_set(self):
        self.slp.lang_fields = set(PREFER_TEST_DICT.keys())
        self.slp.search_params = SearchParams({})
        self.slp.out_dict = copy.deepcopy(PREFER_TEST_DICT)
        self.slp.prefer_lang()
        self.assertDictEqual(self.slp.out_dict, PREFER_TEST_DICT)

    def test_prefer_lang_does_modify_out_dict_if_lang_pref_set(self):
        self.slp.lang_fields = set(PREFER_TEST_DICT.keys())
        self.slp.search_params = SearchParams({'lang_pref': 'en'})
        self.slp.out_dict = copy.deepcopy(PREFER_TEST_DICT)
        self.slp.prefer_lang()
        expected_dict = {
            "title": {
                "bridge": {
                    "en": "title goes here",
                },
                "eldis": {
                    "en": "the title goes here"
                }
            }
        }
        self.assertDictEqual(self.slp.out_dict, expected_dict)

    def test_prefer_source_does_not_modify_out_dict_if_source_pref_not_set(self):
        self.slp.source_fields = set(PREFER_TEST_DICT.keys())
        self.slp.search_params = SearchParams({})
        self.slp.out_dict = copy.deepcopy(PREFER_TEST_DICT)
        self.slp.prefer_source()
        self.assertDictEqual(self.slp.out_dict, PREFER_TEST_DICT)

    def test_prefer_source_does_modify_out_dict_if_source_pref_set(self):
        self.slp.source_fields = set(PREFER_TEST_DICT.keys())
        self.slp.search_params = SearchParams({'source_pref': 'bridge'})
        self.slp.out_dict = copy.deepcopy(PREFER_TEST_DICT)
        self.slp.prefer_source()
        expected_dict = {
            "title": {
                "bridge": {
                    "en": "title goes here",
                    "fr": "le title est ici"
                },
            }
        }
        self.assertDictEqual(self.slp.out_dict, expected_dict)

    def test_exclude_source_includes_source_if_source_only_not_set(self):
        self.slp.search_params = SearchParams({})
        self.assertFalse(self.slp.exclude_source('eldis'))

    def test_exclude_source_includes_source_if_source_only_is_same(self):
        self.slp.search_params = SearchParams({'source_only': 'eldis'})
        self.assertFalse(self.slp.exclude_source('eldis'))

    def test_exclude_source_excludes_source_if_source_only_is_different(self):
        self.slp.search_params = SearchParams({'source_only': 'ella'})
        self.assertTrue(self.slp.exclude_source('eldis'))


TEST_SHORT_FIELDS = list(ObjectDataFilter.short_field_list)
TEST_CORE_FIELDS = ['hub_this', 'hub_that', 'hub_other']
TEST_GENERAL_FIELDS = TEST_CORE_FIELDS + ['author', 'publisher', 'site']
TEST_ADMIN_ONLY_FIELDS = ['deleted', 'legacy_id']

BIG_RESULTS = {
    'object_id': 44,
    'item_id': 44,
    'object_type': 'documents',
    'item_type': 'documents',
    'title': 'some big long thing',
    'hub_this': 'hub44',
    'author': 'Einstein',
    'not_general': 'details',
    'publisher': 'John Pub',
    'deleted': 'false'
}


class ObjectDataFilterTests(TestCase):

    def setUp(self):
        self.odf = ObjectDataFilter(SearchParams({}))
        self.user_level_info = {
            'general_fields_only': False,
            'hide_admin_fields': False,
        }

    def test_filter_results_raises_when_invalid_output_format(self):
        with self.assertRaises(InvalidOutputFormat) as context:
            self.odf.filter_results({}, 'invalid', self.user_level_info)
        self.assertTrue("you gave 'invalid'" in str(context.exception))

    def test_filter_results_for_output_format_id_only_returns_object_id(self):
        result = {
            'a': 1,
            'b': 2,
            'object_id': 3,
            'item_id': 4
        }
        actual = self.odf.filter_results(result, 'id', self.user_level_info)
        expected = {'object_id': 3}
        self.assertDictEqual(actual, expected)

    def test_filter_results_for_output_format_id_uses_item_id_if_object_id_not_available(self):
        result = {
            'a': 1,
            'b': 2,
            'item_id': 4
        }
        actual = self.odf.filter_results(result, 'id', self.user_level_info)
        expected = {'object_id': 4}
        self.assertDictEqual(actual, expected)

    def test_filter_results_for_output_format_id_ignores_extra_fields(self):
        result = {
            'a': 1,
            'object_id': 3,
        }
        self.odf = ObjectDataFilter(SearchParams({'extra_fields': 'a'}))
        actual = self.odf.filter_results(result, 'id', self.user_level_info)
        expected = {'object_id': 3}
        self.assertDictEqual(actual, expected)

    def test_filter_results_returns_all_short_fields_for_all_short_specifiers(self):
        for output_format in ('short', '', None):
            actual = self.odf.filter_results(BIG_RESULTS, output_format, self.user_level_info)
            self.assertSetEqual(set(actual.keys()), set(ObjectDataFilter.short_field_list))

    def test_filter_results_for_output_format_short_includes_extra_fields(self):
        result = {
            'a': 1,
            'object_id': 3,
            'object_type': 'Document',
            'title': 'awesome doc',
        }
        self.odf = ObjectDataFilter(SearchParams({'extra_fields': 'a'}))
        actual = self.odf.filter_results(result, 'short', self.user_level_info)
        self.assertDictEqual(actual, result)

    def test_filter_results_for_output_format_short_uses_backup_values(self):
        result = {
            'item_id': 3,
            'item_type': 'Document',
            'name': 'awesome doc',
        }
        actual = self.odf.filter_results(result, 'short', self.user_level_info)
        expected = {
            'item_id': 3,
            'item_type': 'Document',
            'object_id': 3,
            'object_type': 'Document',
            'title': 'awesome doc',
        }
        self.assertDictEqual(actual, expected)

    @override_settings(CORE_FIELDS=TEST_CORE_FIELDS + TEST_SHORT_FIELDS)
    def test_filter_results_for_output_format_core_returns_all_core_fields(self):
        actual = self.odf.filter_results(BIG_RESULTS, 'core', self.user_level_info)
        self.assertSetEqual(
            set(actual.keys()),
            set(BIG_RESULTS.keys()) & set(TEST_CORE_FIELDS + TEST_SHORT_FIELDS)
        )

    def test_filter_results_for_output_format_full_returns_all_fields(self):
        actual = self.odf.filter_results(BIG_RESULTS, 'full', self.user_level_info)
        self.assertDictEqual(actual, BIG_RESULTS)

    @override_settings(GENERAL_FIELDS=TEST_GENERAL_FIELDS + TEST_SHORT_FIELDS)
    def test_filter_resulst_for_output_format_full_for_general_user(self):
        user_level_info = {
            'general_fields_only': True,
            'hide_admin_fields': True,
        }
        actual = self.odf.filter_results(BIG_RESULTS, 'full', user_level_info)
        self.assertSetEqual(
            set(actual.keys()),
            set(BIG_RESULTS.keys()) & set(TEST_GENERAL_FIELDS + TEST_SHORT_FIELDS)
        )

    @override_settings(ADMIN_ONLY_FIELDS=TEST_ADMIN_ONLY_FIELDS)
    def test_filter_resulst_for_output_format_full_for_non_admin_user(self):
        user_level_info = {
            'general_fields_only': False,
            'hide_admin_fields': True,
        }
        actual = self.odf.filter_results(BIG_RESULTS, 'full', user_level_info)
        self.assertSetEqual(
            set(actual.keys()),
            set(BIG_RESULTS.keys()) - set(TEST_ADMIN_ONLY_FIELDS)
        )


class MetaDataURLCreatorTests(TestCase):

    def setUp(self):
        self.metadata = MetaDataURLCreator('documents', 789, 'hub')

    def get_base_url(self, url_name='object', object_type='documents', object_id=789):
        return reverse(
            url_name,
            kwargs={
                'object_type': object_type,
                'object_id': object_id,
                'output_format': 'full',
                'site': 'hub'
            }
        )

    def test_create_url_with_no_arguments(self):
        expected = self.get_base_url() + '/'
        actual = self.metadata.create_url()
        self.assertEqual(actual, expected)

    def test_create_url_appends_name_in_url_friendly_format(self):
        expected = self.get_base_url() + '/expecting-childbirth-in-africa/'
        actual = self.metadata.create_url(object_name='Expecting - childbirth in Africa. ')
        self.assertEqual(actual, expected)

    def test_create_url_with_object_id_and_type(self):
        expected = self.get_base_url(object_type='Country', object_id=1234) + '/'
        actual = self.metadata.create_url(object_type='Country', object_id=1234)
        self.assertEqual(actual, expected)

    def test_create_url_with_url_name_specified(self):
        expected = self.get_base_url(url_name='category_children') + '/'
        actual = self.metadata.create_url(url_name='category_children')
        self.assertEqual(actual, expected)

    def test_add_url_to_item_if_keys_available_does_nothing_when_item_is_string(self):
        item = 'a string'
        self.metadata.add_url_to_item_if_keys_available(item)
        # the test is really that it doesn't cause an exception
        # but don't catch the exception so we will see the full stack trace

    def test_add_url_to_item_if_keys_available_does_nothing_when_all_keys_not_available(self):
        for item in [
            {},
            {'object_type': 'Document', 'object_name': 'Expecting'},
            {'object_id': 789, 'object_name': 'Expecting'},
            {'object_id': 789, 'object_type': 'Document'},
        ]:
            self.metadata.add_url_to_item_if_keys_available(item)
            self.assertNotIn('metadata_url', item)

    def test_add_url_to_item_if_keys_available_adds_url_when_all_keys_not_available(self):
        item = {'object_id': 789, 'object_type': 'Document', 'object_name': 'Expecting'}
        self.metadata.add_url_to_item_if_keys_available(item)
        self.assertEqual(item['metadata_url'], self.get_base_url() + '/expecting/')
