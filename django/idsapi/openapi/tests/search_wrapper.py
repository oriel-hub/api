from django.utils import unittest
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.conf import settings
from openapi.search_builder import SearchWrapper, InvalidQueryError

class MockSolrInterface:
    def __init__(self, site_url=None):
        self.site_url = site_url

    def query(self, *args, **kwargs):
        self.query = MockSolrQuery()
        return self.query

class MockSolrQuery:
    def __init__(self):
        self.query_call_count = 0
        self.query_args = []
        self.field_list = None

    def query(self, *args, **kwargs):
        self.query_call_count += 1
        self.query_args.append([args, kwargs])

    def field_limit(self, field_list):
        self.field_list = field_list

class SearchWrapperTests(unittest.TestCase):
    def setUp(self):
        self.msi = MockSolrInterface()

    def test_general_user_can_not_request_field_not_in_whitelist(self):
        sw = SearchWrapper('General User', 'eldis', self.msi)

        extra_field = 'contact_position'
        self.assertTrue(extra_field not in settings.GENERAL_FIELDS)
        self.assertTrue(extra_field not in settings.ADMIN_ONLY_FIELDS)

        self.assertRaises(InvalidQueryError, sw.restrict_fields_returned, 'short', {'extra_fields': extra_field})

    def test_partner_user_can_request_field_not_in_whitelist(self):
        sw = SearchWrapper('Partner', 'eldis', self.msi)

        extra_field = 'contact_position'
        self.assertTrue(extra_field not in settings.GENERAL_FIELDS)
        self.assertTrue(extra_field not in settings.ADMIN_ONLY_FIELDS)

        sw.restrict_fields_returned('short', {'extra_fields': extra_field})
        self.assertTrue(extra_field in self.msi.query.field_list)

    def test_partner_user_can_not_request_admin_only_field(self):
        sw = SearchWrapper('Partner', 'eldis', self.msi)

        extra_field = 'legacy_id'
        self.assertTrue(extra_field in settings.ADMIN_ONLY_FIELDS)

        self.assertRaises(InvalidQueryError, sw.restrict_fields_returned, 'short', {'extra_fields': extra_field})

    def test_admin_user_can_request_field_admin_only_field(self):
        sw = SearchWrapper('Unlimited', 'eldis', self.msi)

        extra_field = 'legacy_id'
        self.assertTrue(extra_field in settings.ADMIN_ONLY_FIELDS)

        sw.restrict_fields_returned('short', {'extra_fields': extra_field})
        self.assertTrue(extra_field in self.msi.query.field_list)
