from django.utils import unittest
from django.conf import settings
from openapi.search_builder import SearchWrapper, InvalidFieldError, InvalidQueryError

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
        self.sort_field = None
        self.has_free_text_query = False

    def query(self, *args, **kwargs):
        self.query_call_count += 1
        self.query_args.append([args, kwargs])

    def field_limit(self, field_list):
        self.field_list = field_list

    def sort_by(self, sort_field):
        self.sort_field = sort_field

class SearchWrapperTests(unittest.TestCase):
    def setUp(self):
        self.msi = MockSolrInterface()

    def test_general_user_can_not_request_field_not_in_whitelist(self):
        sw = SearchWrapper('General User', 'eldis', self.msi)

        extra_field = 'contact_position'
        self.assertTrue(extra_field not in settings.GENERAL_FIELDS)
        self.assertTrue(extra_field not in settings.ADMIN_ONLY_FIELDS)

        self.assertRaises(InvalidFieldError, sw.restrict_fields_returned, 'short', {'extra_fields': extra_field})

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

        self.assertRaises(InvalidFieldError, sw.restrict_fields_returned, 'short', {'extra_fields': extra_field})

    def test_admin_user_can_request_field_admin_only_field(self):
        sw = SearchWrapper('Unlimited', 'eldis', self.msi)

        extra_field = 'legacy_id'
        self.assertTrue(extra_field in settings.ADMIN_ONLY_FIELDS)

        sw.restrict_fields_returned('short', {'extra_fields': extra_field})
        self.assertTrue(extra_field in self.msi.query.field_list)

class SearchWrapperAddSortTests(unittest.TestCase):
    def setUp(self):
        self.msi = MockSolrInterface()
        settings.SORT_MAPPING = {'dummy': 'dummy_sort'}

    def test_add_sort_method_disallows_mixed_asc_and_desc_sort(self):
        sw = SearchWrapper('General User', 'eldis', self.msi)
        search_params = {'sort_asc': 'title', 'sort_desc': 'title'}
        self.assertRaises(InvalidQueryError, sw.add_sort, search_params, 'assets')

    def test_add_descending_sort_inverts_field(self):
        sw = SearchWrapper('General User', 'eldis', self.msi)
        sw.add_sort({'sort_desc': 'title'}, 'assets')
        self.assertEquals(self.msi.query.sort_field, '-title')

    def test_add_sort_with_no_mapping(self):
        sw = SearchWrapper('General User', 'eldis', self.msi)
        sw.add_sort({'sort_asc': 'title'}, 'assets')
        self.assertEquals(self.msi.query.sort_field, 'title')

    def test_add_sort_with_mapping(self):
        """
        Sort parameters should be overridable by the user via a mapping dictionary.
        """
        settings.SORT_MAPPING = {'title': 'title_sort'}
        sw = SearchWrapper('General User', 'eldis', self.msi)
        sw.add_sort({'sort_asc': 'title'}, 'assets')
        self.assertEquals(self.msi.query.sort_field, 'title_sort')

    def test_add_sort_default_ordering_when_no_sort_params(self):
        """
        If there are no sort parameters in the request AND there is no free
        text query, the sort order is determined using the sort object mapping.

        Sort field mapping should still take place.
        """
        settings.DEFAULT_SORT_OBJECT_MAPPING = {
            'countries':
                {'field': 'title', 'ascending': True},
        }
        settings.SORT_MAPPING = {'title': 'title_sort'}
        sw = SearchWrapper('General User', 'eldis', self.msi)
        sw.add_sort(dict(), 'countries')
        self.assertEquals(self.msi.query.sort_field, 'title_sort')

    def test_add_sort_no_default_ordering_when_free_text_query(self):
        """
        Free text queries should have no default sort order set.
        """
        settings.DEFAULT_SORT_FIELD = 'title'
        settings.DEFAULT_SORT_ASCENDING = True
        settings.SORT_MAPPING = {'title': 'title_sort'}
        sw = SearchWrapper('General User', 'eldis', self.msi)
        sw.has_free_text_query = True
        sw.add_sort(dict(), 'assets')
        self.assertIsNone(self.msi.query.sort_field)

    def test_add_sort_allows_ordering_when_free_text_query(self):
        """
        Free text queries should still be sortable if a sort order is specified.
        """
        settings.DEFAULT_SORT_FIELD = 'title'
        settings.DEFAULT_SORT_ASCENDING = True
        settings.SORT_MAPPING = {'title': 'title_sort'}
        sw = SearchWrapper('General User', 'eldis', self.msi)
        sw.has_free_text_query = True
        sw.add_sort({'sort_desc': 'title'}, 'assets')
        self.assertEquals(self.msi.query.sort_field, '-title_sort')
