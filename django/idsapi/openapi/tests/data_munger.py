# tests for the data munger
from django.test.testcases import TestCase
from django.test.utils import override_settings

from ..data import DataMunger


class DataMungerTests(TestCase):

    def setUp(self):
        self.data = DataMunger('hub', {})

    def test_convert_facet_string(self):
        test_string = "1200|Country|South Africa"
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['item_id'], '1200')
        self.assertEquals(facet_dict['item_type'], 'Country')
        self.assertEquals(facet_dict['item_name'], 'South Africa')
        self.assertTrue(facet_dict['metadata_url'].endswith('/v1/hub/get/countries/1200/full/south-africa/'),
            "Got %s" % facet_dict['metadata_url'])

    def test_convert_facet_string_with_xml_field(self):
        test_string = "<theme><item_id>563</item_id><item_type>theme</item_type><item_name>Health Challenges</item_name><level>1</level></theme>"
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['item_id'], '563')
        self.assertEquals(facet_dict['item_type'], 'theme')
        self.assertEquals(facet_dict['item_name'], 'Health Challenges')
        self.assertEquals(facet_dict['level'], '1')
        self.assertTrue(facet_dict['metadata_url'].endswith('/v1/hub/get/themes/563/full/health-challenges/'),
            "Got %s" % facet_dict['metadata_url'])

    def test_convert_empty_facet_string_returns_dict_with_empty_values(self):
        test_string = ""
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['item_id'], '')
        self.assertEquals(facet_dict['item_type'], '')
        self.assertEquals(facet_dict['item_name'], '')
        self.assertEquals(facet_dict['metadata_url'], '')

    def test_convert_old_style_facet_string_returns_dict_with_just_item_name(self):
        test_string = "environmental statistics"
        facet_dict = self.data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['item_id'], '')
        self.assertEquals(facet_dict['item_type'], '')
        self.assertEquals(facet_dict['item_name'], 'environmental statistics')
        self.assertEquals(facet_dict['metadata_url'], '')

    def test_field_type_prefix_with_field_name_with_no_underscore(self):
        prefix, source, lang = self.data.field_type_prefix('content')
        self.assertEqual('content', prefix)
        self.assertIsNone(source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_id_field(self):
        prefix, source, lang = self.data.field_type_prefix('item_id')
        self.assertEqual('item_id', prefix)
        self.assertIsNone(source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_field_in_generic_field_list_setting(self):
        with override_settings(GENERIC_FIELD_LIST=['metadata_languages']):
            prefix, source, lang = self.data.field_type_prefix('metadata_languages')
        self.assertEqual('metadata_languages', prefix)
        self.assertIsNone(source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_source_but_no_language(self):
        prefix, source, lang = self.data.field_type_prefix('et_al_eldis_zz')
        self.assertEqual('et_al', prefix)
        self.assertEqual('eldis', source)
        self.assertIsNone(lang)

    def test_field_type_prefix_with_field_name_with_source_and_language(self):
        prefix, source, lang = self.data.field_type_prefix('title_eldis_en')
        self.assertEqual('title', prefix)
        self.assertEqual('eldis', source)
        self.assertEqual('en', lang)

    def test_create_source_lang_dict_works(self):
        result = {
            "item_id": 1234,
            "et_al_bridge_zz": "some people",
            "et_al_eldis_zz": "similar people",
            "title_bridge_en": "title goes here",
            "title_bridge_fr": "le title est ici",
            "title_eldis_en": "the title goes here",
        }
        expected_dict = {
            "item_id": 1234,
            "et_al": {
                "bridge": "some people",
                "eldis": "similar people"
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
        with override_settings(GENERIC_FIELD_LIST=['item_id']):
            actual_dict = self.data.create_source_lang_dict(result)
        self.assertDictEqual(expected_dict, actual_dict)
