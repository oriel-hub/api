# tests for the data munger
import copy

from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.test.utils import override_settings
from openapi.data import DataMunger


@override_settings(FACET_TYPES={
    'theme': "xml_string",
    'country': 'id_name_type',
    'keyword': 'plain_string',
})
class DataMungerTests(TestCase):

    def setUp(self):
        self.data = DataMunger('hub', SearchParams({}))
        self.data.metadata = MetaDataURLCreator('Document', '789', 'hub')

    def assert_endswith(self, full_string, expected_end):
        self.assertTrue(full_string.endswith(expected_end),
                        'Got: %s\nExpected end: %s' % (full_string, expected_end))

    def test_convert_facet_string(self):
        test_string = "A1200|Country|South Africa"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, "country")

        self.assertEqual(facet_dict['object_id'], 'A1200')
        self.assertEqual(facet_dict['object_type'], 'Country')
        self.assertEqual(facet_dict['object_name'], 'South Africa')
        self.assertTrue(facet_dict['metadata_url'].endswith('/openapi/eldis/get/countries/A1200/full/south-africa/'),
            "Got %s" % facet_dict['metadata_url'])

    def test_convert_facet_string_with_xml_field(self):
        test_string = "<theme><object_id>C563</object_id><object_type>theme</object_type><object_name>Health Challenges</object_name><level>1</level></theme>"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, "theme")

        self.assertEqual(facet_dict['object_id'], 'C563')
        self.assertEqual(facet_dict['object_type'], 'theme')
        self.assertEqual(facet_dict['object_name'], 'Health Challenges')
        self.assertEqual(facet_dict['level'], '1')
        self.assertTrue(facet_dict['metadata_url'].endswith('/openapi/eldis/get/themes/C563/full/health-challenges/'),
            "Got %s" % facet_dict['metadata_url'])

    def test_convert_empty_facet_string_returns_dict_with_empty_values(self):
        test_string = ""
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, "keyword")

        self.assertEqual(facet_dict['object_id'], '')
        self.assertEqual(facet_dict['object_type'], '')
        self.assertEqual(facet_dict['object_name'], '')
        self.assertEqual(facet_dict['metadata_url'], '')

    def test_convert_old_style_facet_string_returns_dict_with_just_object_name(self):
        test_string = "environmental statistics"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, "keyword")

        self.assertEqual(facet_dict['object_id'], '')
        self.assertEqual(facet_dict['object_type'], '')
        self.assertEqual(facet_dict['object_name'], 'environmental statistics')
        self.assertEqual(facet_dict['metadata_url'], '')
