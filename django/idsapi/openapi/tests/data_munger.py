# tests for the data munger
from django.test.testcases import TestCase
from openapi.data import DataMunger

class DataMungerTests(TestCase):

    def test_convert_facet_string(self):
        test_string = "C548|theme|Decentralisation & Local Governance"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], 'C548')
        self.assertEquals(facet_dict['object_type'], 'theme')
        self.assertEquals(facet_dict['object_name'], 'Decentralisation & Local Governance')
        self.assertTrue(facet_dict['metadata_url'].endswith('/openapi/eldis/get/theme/C548/full/decentralisation-local-governance/'),
            "Got %s" % facet_dict['metadata_url'])


    def test_convert_empty_facet_string_returns_dict_with_empty_values(self):
        test_string = ""
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], '')
        self.assertEquals(facet_dict['object_type'], '')
        self.assertEquals(facet_dict['object_name'], '')
        self.assertEquals(facet_dict['metadata_url'], '')


    def test_convert_old_style_facet_string_returns_dict_with_just_object_name(self):
        test_string = "environmental statistics"
        data = DataMunger("eldis")
        facet_dict = data.convert_facet_string(test_string)

        self.assertEquals(facet_dict['object_id'], '')
        self.assertEquals(facet_dict['object_type'], '')
        self.assertEquals(facet_dict['object_name'], 'environmental statistics')
        self.assertEquals(facet_dict['metadata_url'], '')
