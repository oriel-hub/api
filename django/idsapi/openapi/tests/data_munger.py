# tests for the data munger
import copy

from django.test.testcases import TestCase
from django.test.utils import override_settings

from ..search_builder import SearchParams
from ..data import DataMunger, SourceLangParser

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
        self.data = DataMunger('hub', {})

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
