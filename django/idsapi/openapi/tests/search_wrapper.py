from django.utils import unittest
from django.conf import settings
import sunburnt

from openapi.search_builder import (
    SearchBuilder,
    SearchWrapper,
    SearchParams,
    FacetArgs,
    InvalidFieldError,
    InvalidQueryError,
    UnknownQueryParamError
)

DEFAULT_SEARCH_TERM = 'water'


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
        self.extra = {}
        self.filter_args = {}

    def query(self, *args, **kwargs):
        self.query_call_count += 1
        self.query_args.append([args, kwargs])
        return self

    def field_limit(self, field_list):
        self.field_list = field_list
        return self

    def sort_by(self, sort_field):
        self.sort_field = sort_field
        return self

    def add_extra(self, **kwargs):
        self.extra.update(kwargs)
        return self

    def filter(self, **kwargs):
        self.filter_args.update(kwargs)
        return self


class SearchBuilderTests(unittest.TestCase):
    def setup(self):
        self.msi = MockSolrInterface()
        self.sb = self.get_search_builder(solr=self.msi)

    def get_search_builder(self, user_level='General User', site='hub', solr=None):
        return SearchBuilder(user_level, site, solr)


class SearchWrapperTests(unittest.TestCase):
    def setUp(self):
        self.msi = MockSolrInterface()

    def test_general_user_can_not_request_field_not_in_whitelist(self):
        sw = SearchWrapper('General User', 'hub', self.msi)

        extra_field = 'contact_position'
        self.assertNotIn(extra_field, settings.GENERAL_FIELDS)
        self.assertNotIn(extra_field, settings.ADMIN_ONLY_FIELDS)

        self.assertRaises(InvalidFieldError, sw.restrict_fields_returned, 'short', {'extra_fields': extra_field})

    def test_partner_user_can_not_request_admin_only_field(self):
        sw = SearchWrapper('Partner', 'hub', self.msi)

        extra_field = 'legacy_id'
        self.assertTrue(extra_field in settings.ADMIN_ONLY_FIELDS)

        self.assertRaises(InvalidFieldError, sw.restrict_fields_returned, 'short', {'extra_fields': extra_field})

    # TODO: replace with data munger test
    # def test_partner_user_can_request_field_not_in_whitelist(self):
    #    sw = SearchWrapper('Partner', 'hub', self.msi)

    #    extra_field = 'contact_position'
    #    self.assertNotIn(extra_field, settings.GENERAL_FIELDS)
    #    self.assertNotIn(extra_field, settings.ADMIN_ONLY_FIELDS)

    #    sw.restrict_fields_returned('short', {'extra_fields': extra_field})
    #    self.assertTrue(extra_field in self.msi.query.field_list)

    # TODO: replace with data munger test
    # def test_admin_user_can_request_field_admin_only_field(self):
    #    sw = SearchWrapper('Unlimited', 'hub', self.msi)

    #    extra_field = 'legacy_id'
    #    self.assertTrue(extra_field in settings.ADMIN_ONLY_FIELDS)

    #    sw.restrict_fields_returned('short', {'extra_fields': extra_field})
    #    self.assertTrue(extra_field in self.msi.query.field_list)


class SearchWrapperAddSortTests(unittest.TestCase):
    def setUp(self):
        self.msi = MockSolrInterface()
        settings.SORT_MAPPING = {'dummy': 'dummy_sort'}

    def set_sort_mapping(self, site, mapping):
        self.orig_sort_mapping = settings.SORT_MAPPING.copy()
        settings.SORT_MAPPING = mapping

    def unset_sort_mapping(self, site):
        settings.SORT_MAPPING = self.orig_sort_mapping

    def test_add_sort_method_disallows_mixed_asc_and_desc_sort(self):
        sw = SearchWrapper('General User', 'hub', self.msi)
        search_params = {'sort_asc': 'title', 'sort_desc': 'title'}
        self.assertRaises(InvalidQueryError, sw.add_sort, search_params, 'assets')

    def test_add_descending_sort_inverts_field(self):
        sw = SearchWrapper('General User', 'hub', self.msi)
        sw.add_sort({'sort_desc': 'publication_date'}, 'assets')
        self.assertEquals(self.msi.query.sort_field, '-publication_date')

    def test_add_sort_with_no_mapping(self):
        sw = SearchWrapper('General User', 'hub', self.msi)
        sw.add_sort({'sort_asc': 'publication_date'}, 'assets')
        self.assertEquals(self.msi.query.sort_field, 'publication_date')

    def test_add_sort_with_mapping(self):
        """
        Sort parameters should be overridable by the user via a mapping dictionary.
        """
        self.set_sort_mapping('hub', {'title': 'title_sort'})
        try:
            sw = SearchWrapper('General User', 'hub', self.msi)
            sw.add_sort({'sort_asc': 'title'}, 'assets')
            self.assertEquals(self.msi.query.sort_field, 'title_sort')
        finally:
            self.unset_sort_mapping('hub')

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
        self.set_sort_mapping('hub', {'title': 'title_sort'})
        try:
            sw = SearchWrapper('General User', 'hub', self.msi)
            sw.add_sort(dict(), 'countries')
            self.assertEquals(self.msi.query.sort_field, 'title_sort')
        finally:
            self.unset_sort_mapping('hub')

    def test_add_sort_no_default_ordering_when_free_text_query(self):
        """
        Free text queries should have no default sort order set.
        """
        settings.DEFAULT_SORT_FIELD = 'title'
        settings.DEFAULT_SORT_ASCENDING = True
        self.set_sort_mapping('hub', {'title': 'title_sort'})
        try:
            sw = SearchWrapper('General User', 'hub', self.msi)
            sw.has_free_text_query = True
            sw.add_sort(dict(), 'assets')
            self.assertIsNone(self.msi.query.sort_field)
        finally:
            self.unset_sort_mapping('hub')

    def test_add_sort_allows_ordering_when_free_text_query(self):
        """
        Free text queries should still be sortable if a sort order is specified.
        """
        settings.DEFAULT_SORT_FIELD = 'title'
        settings.DEFAULT_SORT_ASCENDING = True
        self.set_sort_mapping('hub', {'title': 'title_sort'})
        try:
            sw = SearchWrapper('General User', 'hub', self.msi)
            sw.has_free_text_query = True
            sw.add_sort({'sort_desc': 'title'}, 'assets')
            self.assertEquals(self.msi.query.sort_field, '-title_sort')
        finally:
            self.unset_sort_mapping('hub')


class SearchWrapperAddFieldQueryTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # TODO: there doesn't seem to be a easy way to just test the query
        # building behaviour with out building a real connection.
        cls.si = sunburnt.SolrInterface(settings.BASE_URL)

    def setUp(self):
        self.sw = SearchWrapper('General User', 'hub', SearchWrapperAddFieldQueryTests.si)

    def test_field_query_supports_unicode_text(self):
        q = self.sw.add_field_query('title', u'C\xf4tedivorie')
        self.assertEquals(u'title:C\xf4tedivorie', q.options()[None])

    def test_field_query_supports_quoted_text(self):
        q = self.sw.add_field_query('title', '"beyond their age"')
        self.assertEquals(u'title:"beyond their age"', q.options()[None])

    def test_field_query_supports_quoted_text_with_or(self):
        q = self.sw.add_field_query('title', '"beyond their age"|climate')
        self.assertEquals(u'title:"beyond their age" OR title:climate', q.options()[None])

    def test_field_query_supports_quoted_text_with_and(self):
        q = self.sw.add_field_query('title', '"beyond their age"&"climate change"')
        self.assertEquals(u'title:"beyond their age" AND title:"climate change"', q.options()[None])

    def test_field_query_supports_pipe_in_quoted_text(self):
        q = self.sw.add_field_query('title', '"beyond|their age"')
        self.assertEquals(u'title:"beyond\\|their age"', q.options()[None])

    def test_field_query_supports_ampersand_in_quoted_text(self):
        q = self.sw.add_field_query('title', '"beyond&their age"')
        self.assertEquals(u'title:"beyond\\&their age"', q.options()[None])

    def test_field_query_supports_quoted_text_with_and_aswell_as_pipe_in_quotes(self):
        q = self.sw.add_field_query('title', '"beyond their age"&"climate|change"')
        self.assertEquals(u'title:"beyond their age" AND title:"climate\\|change"', q.options()[None])

    def test_field_query_supports_quoted_text_with_or_aswell_as_ampersand_in_quotes(self):
        q = self.sw.add_field_query('title', '"beyond their age"|"climate&change"')
        self.assertEquals(u'title:"beyond their age" OR title:"climate\\&change"', q.options()[None])

    def test_field_query_checks_quoted_text_is_closed(self):
        self.assertRaises(InvalidQueryError, self.sw.add_field_query, 'title', '"beyond their age')

    def test_field_query_supports_not_query(self):
        q = self.sw.add_field_query('country', '!Angola')
        self.assertEquals(u'NOT country:Angola', q.options()[None])

    def test_field_query_supports_not_with_quoted_text(self):
        q = self.sw.add_field_query('title', '!"beyond their age"')
        self.assertEquals(u'NOT title:"beyond their age"', q.options()[None])

    def test_field_query_supports_quoted_text_with_or_not(self):
        q = self.sw.add_field_query('title', '"beyond their age"|!climate')
        # the (*:* AND ...) is added by sunburnt, so live with it
        self.assertEquals(u'title:"beyond their age" OR (*:* AND NOT title:climate)', q.options()[None])

    def test_field_query_supports_quoted_text_with_and_not(self):
        q = self.sw.add_field_query('title', '"beyond their age"&!"climate change"')
        self.assertEquals(u'title:"beyond their age" AND NOT title:"climate change"', q.options()[None])

    def test_split_string_around_quotes_and_delimiters_works_not_splitting(self):
        self.assertEqual(['simple'],
            self.sw.split_string_around_quotes_and_delimiters('simple'))

    def test_split_string_around_quotes_and_delimiters_works_simple_split(self):
        self.assertEqual(['simple', '|', 'split'],
            self.sw.split_string_around_quotes_and_delimiters('simple|split'))
        self.assertEqual(['simple', '&', 'split'],
            self.sw.split_string_around_quotes_and_delimiters('simple&split'))
        self.assertEqual(['simple', '&', 'split', '|', '2'],
            self.sw.split_string_around_quotes_and_delimiters('simple&split|2'))

    def test_split_string_around_quotes_and_delimiters_does_not_split_inside_quotes(self):
        self.assertEqual(['"simple|split"'],
            self.sw.split_string_around_quotes_and_delimiters('"simple|split"'))
        self.assertEqual(['"simple&split"'],
            self.sw.split_string_around_quotes_and_delimiters('"simple&split"'))

    def test_split_string_around_quotes_and_delimiters_does_not_split_inside_quotes_but_does_outside(self):
        self.assertEqual(['"simple|split"', '|', 'test'],
            self.sw.split_string_around_quotes_and_delimiters('"simple|split"|test'))
        self.assertEqual(['"simple&split"', '&', 'test'],
            self.sw.split_string_around_quotes_and_delimiters('"simple&split"&test'))

    def test_split_string_around_quotes_and_delimiters_with_complicated_string(self):
        self.assertEqual(['"complex|split&ting"', '|', 'another', '|', 'bit', '|', '"or two"'],
            self.sw.split_string_around_quotes_and_delimiters('"complex|split&ting"|another | bit|"or two"'))
        self.assertEqual(['"complex|split&ting"', '&', 'another', '&', 'bit', '&', '"or two"'],
            self.sw.split_string_around_quotes_and_delimiters('"complex|split&ting"& another & bit&"or two"'))
        self.assertEqual(['"complex|split&ting"', '|', 'another', '&', 'bit', '&', '"or two"'],
            self.sw.split_string_around_quotes_and_delimiters('"complex|split&ting"| another & bit&"or two"'))

    def test_split_string_around_quotes_and_delimiters_works_not_splitting_with_bang(self):
        self.assertEqual(['!simple'],
            self.sw.split_string_around_quotes_and_delimiters('!simple'))

    def test_split_string_around_quotes_and_delimiters_works_simple_split_with_bang(self):
        self.assertEqual(['!simple', '|', 'split'],
            self.sw.split_string_around_quotes_and_delimiters('!simple|split'))
        self.assertEqual(['simple', '&', '!split'],
            self.sw.split_string_around_quotes_and_delimiters('simple&!split'))
        self.assertEqual(['simple', '&', '!split', '|', '2'],
            self.sw.split_string_around_quotes_and_delimiters('simple&!split|2'))

    # TODO: bang before quotation marks
    def test_split_string_around_quotes_and_delimiters_does_not_split_inside_quotes_with_bang(self):
        self.assertEqual(['!"simple|split"'],
            self.sw.split_string_around_quotes_and_delimiters('!"simple|split"'))
        self.assertEqual(['!"simple&split"'],
            self.sw.split_string_around_quotes_and_delimiters('!"simple&split"'))

    def test_split_string_around_quotes_and_delimiters_does_not_split_inside_quotes_but_does_outside_with_bang(self):
        self.assertEqual(['!"simple|split"', '|', 'test'],
            self.sw.split_string_around_quotes_and_delimiters('!"simple|split"|test'))
        self.assertEqual(['"simple&split"', '&', '!test'],
            self.sw.split_string_around_quotes_and_delimiters('"simple&split"&!test'))

    def test_split_string_around_quotes_and_delimiters_with_complicated_string_with_bang(self):
        self.assertEqual(['!"complex|split&ting"', '|', 'another', '|', 'bit', '|', '"or two"'],
            self.sw.split_string_around_quotes_and_delimiters('!"complex|split&ting"|another | bit|"or two"'))
        self.assertEqual(['"complex|split&ting"', '&', '!another', '&', 'bit', '&', '"or two"'],
            self.sw.split_string_around_quotes_and_delimiters('"complex|split&ting"& !another & bit&"or two"'))
        self.assertEqual(['"complex|split&ting"', '|', 'another', '&', 'bit', '&', '!"or two"'],
            self.sw.split_string_around_quotes_and_delimiters('"complex|split&ting"| another & bit&!"or two"'))


class SearchParamsTests(unittest.TestCase):

    def test_has_query_true_if_any_search_params_present(self):
        sp = SearchParams({'q': DEFAULT_SEARCH_TERM})
        self.assertTrue(sp.has_query())

    def test_has_query_false_if_no_search_params_present(self):
        sp = SearchParams({})
        self.assertFalse(sp.has_query())

    def test_invalid_query_raised_if_start_offset_is_negative(self):
        sp = SearchParams({'start_offset': '-1'})
        self.assertRaises(InvalidQueryError, sp.start_offset)

    def test_invalid_query_raised_if_start_offset_is_non_numeric(self):
        sp = SearchParams({'start_offset': 'not_a_number'})
        self.assertRaises(InvalidQueryError, sp.start_offset)

    def test_invalid_query_raised_if_num_results_is_non_numeric(self):
        sp = SearchParams({'num_results': 'not_a_number'})
        self.assertRaises(InvalidQueryError, sp.num_results)

    def test_invalid_param_returns_true_if_bad_param_present(self):
        sp = SearchParams({'q': DEFAULT_SEARCH_TERM, 'bad_param': 'value'})
        self.assertTrue(sp._invalid_param('bad_param', []))


class FacetArgsTests(unittest.TestCase):
    FACET_MAPPING = {
        't1': 'type1',
        't2': 'type2',
    }

    def test_init_doesnt_raise_error_if_facet_type_is_in_mapping(self):
        try:
            FacetArgs({}, 't1', self.FACET_MAPPING, exclude_zero_count=False)
        except InvalidQueryError:
            self.fail('Unexpected InvalidQueryError raised in FacetArgs.__init__()')

    def test_init_raises_error_if_facet_type_is_not_in_mapping(self):
        self.assertRaises(
            InvalidQueryError,
            FacetArgs,
            search_params=SearchParams({}),
            facet_type='t3',
            facet_mapping=self.FACET_MAPPING,
            exclude_zero_count=False
        )

    def test_args_returns_mapped_facet(self):
        fa = FacetArgs(SearchParams({}), 't1', self.FACET_MAPPING, exclude_zero_count=False)
        self.assertSequenceEqual(['type1'], fa.args())
        fa = FacetArgs(SearchParams({}), 't2', self.FACET_MAPPING, exclude_zero_count=False)
        self.assertSequenceEqual(['type2'], fa.args())

    def test_kwargs_does_not_set_mincount_if_not_exclude_zero_count(self):
        fa = FacetArgs(SearchParams({}), 't1', self.FACET_MAPPING, exclude_zero_count=False)
        kwargs = fa.kwargs()
        self.assertNotIn('mincount', kwargs)

    def test_kwargs_has_mincount_if_exclude_zero_count(self):
        fa = FacetArgs(SearchParams({}), 't1', self.FACET_MAPPING, exclude_zero_count=True)
        kwargs = fa.kwargs()
        self.assertTrue(kwargs['mincount'])

    def test_kwargs_does_not_set_limit_if_num_results_not_in_search_params(self):
        search_params = SearchParams({})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        kwargs = fa.kwargs()
        self.assertNotIn('limit', kwargs)

    def test_kwargs_has_limit_if_num_results_in_search_params(self):
        search_params = SearchParams({'num_results': 7})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        kwargs = fa.kwargs()
        self.assertEqual(7, kwargs['limit'])

    def test_kwargs_ensures_limit_is_int(self):
        search_params = SearchParams({'num_results': '7'})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        kwargs = fa.kwargs()
        self.assertEqual(7, kwargs['limit'])

    def test_kwargs_does_not_set_sort_if_count_sort_not_in_search_params(self):
        search_params = SearchParams({})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        kwargs = fa.kwargs()
        self.assertNotIn('sort', kwargs)

    def test_kwargs_has_sort_if_count_sort_in_search_params(self):
        search_params = SearchParams({'count_sort': 'count_desc'})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        kwargs = fa.kwargs()
        self.assertEqual('count', kwargs['sort'])
        search_params = SearchParams({'count_sort': 'name_asc'})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        kwargs = fa.kwargs()
        self.assertEqual('index', kwargs['sort'])

    def test_kwargs_raises_error_if_count_sort_value_unknown(self):
        search_params = SearchParams({'count_sort': 'bubble'})
        fa = FacetArgs(search_params, 't1', self.FACET_MAPPING, False)
        self.assertRaises(
            InvalidQueryError,
            fa.kwargs,
        )
