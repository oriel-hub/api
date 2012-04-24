# tests for the data munger
from django.test.testcases import TestCase
from openapi.data import DataMunger

class DataMungerTests(TestCase):

    def test_convert_facet_string(self):
        test_string = "A1200|Country|South Africa"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, 'Country')

        self.assertEquals(facet_dict['object_id'], 'A1200')
        self.assertEquals(facet_dict['object_type'], 'countries')
        self.assertEquals(facet_dict['object_name'], 'South Africa')
        self.assertTrue(facet_dict['metadata_url'].endswith('/openapi/eldis/get/countries/A1200/full/south-africa/'),
            "Got %s" % facet_dict['metadata_url'])

    def test_convert_facet_string_with_extra_theme_field(self):
        test_string = "C548|theme|Decentralisation & Local Governance|2"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, 'theme')

        self.assertEquals(facet_dict['object_id'], 'C548')
        self.assertEquals(facet_dict['object_type'], 'themes')
        self.assertEquals(facet_dict['object_name'], 'Decentralisation & Local Governance')
        self.assertEquals(facet_dict['cat_level'], '2')
        self.assertTrue(facet_dict['metadata_url'].endswith('/openapi/eldis/get/themes/C548/full/decentralisation-local-governance/'),
            "Got %s" % facet_dict['metadata_url'])


    def test_convert_empty_facet_string_returns_dict_with_empty_values(self):
        test_string = ""
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, 'country')

        self.assertEquals(facet_dict['object_id'], '')
        self.assertEquals(facet_dict['object_type'], '')
        self.assertEquals(facet_dict['object_name'], '')
        self.assertEquals(facet_dict['metadata_url'], '')


    def test_convert_old_style_facet_string_returns_dict_with_just_object_name(self):
        test_string = "environmental statistics"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string, 'sector')

        self.assertEquals(facet_dict['object_id'], '')
        self.assertEquals(facet_dict['object_type'], '')
        self.assertEquals(facet_dict['object_name'], 'environmental statistics')
        self.assertEquals(facet_dict['metadata_url'], '')
