# a class to build searches
#
# TODO: create a mock version of this class for tests
import logging
import urllib
import urllib2
import re
from datetime import datetime, timedelta
import sunburnt

from django.conf import settings
from djangorestframework.renderers import BaseRenderer

from openapi import defines

# this is a global to cache the Solr instance
saved_solr_interface = {}
solr_interface_created = {}

query_mapping = settings.QUERY_MAPPING

logger = logging.getLogger(__name__)


def get_solr_interface(site):
    """cache the solr interface for an hour at a time so we don't need
    to fetch the schema on every single query."""
    global saved_solr_interface
    global solr_interface_created
    if site != 'hub':
        raise InvalidQueryError("Unknown site: %s" % site)
    if site not in saved_solr_interface:
        too_old = True
    else:
        age = datetime.now() - solr_interface_created[site]
        too_old = age > timedelta(hours=1)
    if too_old:
        try:
            saved_solr_interface[site] = sunburnt.SolrInterface(
                settings.BASE_URL, format='json')
            solr_interface_created[site] = datetime.now()
        except Exception as e:
            msg = 'Solr is not responding (using %s )' % settings.BASE_URL
            logger.error(msg + str(e), exc_info=e)
            raise SolrUnavailableError(msg)
    return saved_solr_interface[site]


class SearchBuilder():

    def __init__(self, user_level, site):
        self.sw = SearchWrapper(user_level, site)

    def _assert_only_one_query_in_query_list(self, query_list, param):
        if len(query_list) > 1:
            raise InvalidQueryError(
                "Cannot repeat query parameters - there is more than one '%s'"
                % param)

    def _assert_query_param_has_value(self, query, param):
        if len(query) < 1:
            raise InvalidQueryError(
                "All query parameters must have a value, but '%s' does not"
                % param)

    def _assert_query_param_can_be_user_with_object_type(self, param, object_type):
        if query_mapping[param]['object_type'] != 'all':
            if query_mapping[param]['object_type'] != object_type:
                raise InvalidQueryError(
                    "Can only use query parameter '%s' with item type '%s', "
                    "your search had item type '%s'"
                    %
                    (param, query_mapping[param]['object_type'], object_type))

    def _assert_valid_query_param(self, param, allowed_param_list):
        if (
            param[0] != '_' and
            param not in allowed_param_list and
            param != BaseRenderer._FORMAT_QUERY_PARAM
        ):
            raise UnknownQueryParamError(param)

    def _is_date_query(self, param):
        for date_prefix in settings.DATE_PREFIX_MAPPING.keys():
            if param.startswith(date_prefix):
                return True
        return False

    def _add_query_via_query_mapping(self, param, object_type, query):
        self._assert_query_param_can_be_user_with_object_type(param, object_type)
        # we might have to search across multiple fields
        if isinstance(query_mapping[param]['solr_field'], list):
            self.sw.add_multifield_parameter_query(query_mapping[param]['solr_field'], query)
        elif param in settings.FQ_FIELDS:
            self.sw.add_filter(query_mapping[param]['solr_field'], query)
        else:
            self.sw.add_parameter_query(query_mapping[param]['solr_field'], query)

    def create_itemid_query(self, object_id, search_params, object_type, output_format):
        for param in search_params:
            self._assert_valid_query_param(param, ['extra_fields'])
        self.sw.si_query = self.sw.solr.query(item_id=object_id)
        self.sw.restrict_search_by_object_type(object_type, allow_objects=True)
        self.sw.restrict_fields_returned(output_format, search_params)
        return self.sw

    def create_search(self, search_params, object_type, output_format, facet_type=None):
        allowed_param_list = [
            'num_results', 'num_results_only', 'start_offset',
            'extra_fields', 'sort_asc', 'sort_desc', 'lang_pref',
            'source_pref', 'count_sort'
        ]
        for param in search_params:
            query_list = search_params.getlist(param)
            self._assert_only_one_query_in_query_list(query_list, param)
            query = query_list[0]
            self._assert_query_param_has_value(query, param)
            if param == 'q':
                self.sw.add_free_text_query(urllib.unquote_plus(query))
            elif param in query_mapping.keys():
                self._add_query_via_query_mapping(param, object_type, query)
            elif self._is_date_query(param):
                self.sw.add_date_query(param, query)
            else:
                # if param not in our list of allowed params
                self._assert_valid_query_param(param, allowed_param_list)

        self.sw.restrict_search_by_object_type(object_type)
        self.sw.restrict_fields_returned(output_format, search_params)
        self.sw.add_sort(search_params, object_type)
        if facet_type is None:
            self.sw.add_paginate(search_params)
        else:
            self.sw.add_facet(facet_type, search_params)
            self.sw.add_paginate({'num_results': 0})
        return self.sw

    def create_all_search(self, search_params, object_type, output_format):
        self.sw.restrict_search_by_object_type(object_type)
        self.sw.restrict_fields_returned(output_format, search_params)
        self.sw.add_sort(search_params, object_type)
        self.sw.add_paginate(search_params)
        return self.sw

    def create_category_children_search(self, search_params, object_type, object_id):
        if object_type not in settings.OBJECT_TYPES_WITH_HIERARCHY:
            raise InvalidQueryError("Item type '%s' does not have children" % object_type)

        # strip the prefix letter off
        self.sw.add_filter('cat_parent', object_id)
        self.sw.restrict_search_by_object_type(object_type)
        self.sw.add_paginate(search_params)
        return self.sw


class SearchWrapper:
    quoted_re = re.compile(r'(!?"[^"]*?")')
    amp_pipe_re = re.compile(r'(\s|[&|]+)')

    def __init__(self, user_level, site, solr=None):
        """
            Args:
                user_level (string): A String representing the user level. Eg 'General User'.
                site (string): A String representing the SOLR site to use. Eg 'eldis' or 'bridge'.
                solr (object): an object to be the solr interface (to allow for mocking)
        """
        if solr is not None:
            self.solr = solr
        else:
            self.solr = get_solr_interface(site)
        self.site = site
        self.si_query = self.solr.query()
        self.si_query = self.si_query.add_extra(defType='edismax')
        self.user_level = user_level
        self.has_free_text_query = False

    def execute(self):
        solr_query = settings.BASE_URL + \
            'select/?' + urllib.urlencode(self.si_query.params())
        if settings.LOG_SEARCH_PARAMS:
            # this will print to console or error log as appropriate
            logger.info("search params: " + self.si_query.params())
            logger.info("solr query: " + solr_query)
        return self.si_query.execute(), solr_query

    def restrict_search_by_object_type(self, object_type, allow_objects=False):
        """
            Args:
                object_type (string): The type of item to search for.
            Kwargs:
                allow_objects (bool): Set for unrestricted search over objects.
        """
        if object_type == 'assets':
            # search for any object_type that is an asset
            self.add_filter_list(settings.SOLR_OBJECT_TYPE, defines.ASSET_NAMES)
        elif allow_objects and object_type == 'objects':
            # don't restrict search and don't raise an Error
            # required for single object search
            pass
        elif object_type in defines.OBJECT_TYPES:
            self.add_filter(settings.SOLR_OBJECT_TYPE, settings.OBJECT_TYPES_TO_OBJECT_NAME[object_type])
        else:
            raise UnknownObjectError(object_type)

    def add_paginate(self, search_params):
        try:
            start_offset = int(search_params['start_offset']) if 'start_offset' in search_params else 0
        except ValueError:
            raise InvalidQueryError("'start_offset' must be a decimal number - you gave %s"
                    % search_params['start_offset'])
        try:
            num_results = int(search_params['num_results']) if 'num_results' in search_params else 10
        except ValueError:
            raise InvalidQueryError("'num_results' must be a decimal number - you gave %s"
                    % search_params['num_results'])
        if start_offset < 0:
            raise InvalidQueryError("'start_offset' cannot be negative - you gave %d" % start_offset)
        if num_results < 0:
            raise InvalidQueryError("'num_results' cannot be negative - you gave %d" % num_results)
        max_results = settings.USER_LEVEL_INFO[self.user_level]['max_items_per_call']
        if max_results != 0 and num_results > max_results:
            raise InvalidQueryError("'num_results' cannot be more than %d - you gave %d"
                    % (max_results, num_results))

        if 'num_results_only' in search_params:
            num_results = 0
        self.si_query = self.si_query.paginate(start=start_offset, rows=num_results)

    def _extract_sort_field_ascending(self, search_params):
        sort_asc = search_params.get('sort_asc')
        sort_desc = search_params.get('sort_desc')
        if sort_asc and sort_desc:
            raise InvalidQueryError("Cannot use both 'sort_asc' and 'sort_desc'")
        ascending = bool(sort_asc)

        sort_field = sort_asc or sort_desc
        if sort_field and sort_field not in settings.SORT_FIELDS:
            raise InvalidQueryError("Sorry, you can't sort by %s" % sort_field)

        return sort_field, ascending

    def _get_default_sort_order(self, object_type):
        sort_field = ascending = None
        if object_type and object_type in defines.OBJECT_TYPES:
            object_default = settings.DEFAULT_SORT_OBJECT_MAPPING.get(object_type)
            if object_default:
                sort_field = object_default['field']
                ascending = object_default['ascending']
        return sort_field, ascending

    def add_sort(self, search_params, object_type):
        """
            Args:
                search_params (dict): A dict like containing the request query string.
                object_type (string): The object type of the request ('asset', 'document, etc).

             do default sort order, but only if no free text query -
             if there is a free text query then the sort order will be by
             score
        """
        sort_field, ascending = self._extract_sort_field_ascending(search_params)

        # free text queries have no default sort ordering
        if not sort_field and self.has_free_text_query:
            return

        # Use default sort ordering when no sort parameter set
        if not sort_field:
            sort_field, ascending = self._get_default_sort_order(object_type)

        # Otherwise assume the catch all default
        if not sort_field:
            sort_field = settings.DEFAULT_SORT_FIELD
            ascending = settings.DEFAULT_SORT_ASCENDING

        sort_field = settings.SORT_MAPPING.get(sort_field, sort_field)
        sort_ord = '' if ascending else '-'

        try:
            self.si_query = self.si_query.sort_by(sort_ord + sort_field)
        except sunburnt.SolrError as e:
            raise InvalidQueryError("Can't do sort on field %s: %s" % (sort_field, e))

    def add_free_text_query(self, search_text):
        self.si_query = self.si_query.query(search_text.lower())

    def add_facet(self, facet_type, search_params):
        fa = FacetArgs(
            search_params,
            facet_type,
            settings.FACET_MAPPING,
            settings.EXCLUDE_ZERO_COUNT_FACETS
        )
        self.si_query = self.si_query.facet_by(*fa.args(), **fa.kwargs())

    def restrict_fields_returned(self, output_format, search_params):
        if output_format not in [None, '', 'id', 'short', 'hub', 'full']:
            raise InvalidOutputFormat(output_format)

        if 'extra_fields' in search_params:
            fields = search_params['extra_fields'].lower().split(' ')
            level_info = settings.USER_LEVEL_INFO[self.user_level]
            for field in fields:
                if level_info['general_fields_only'] and field not in settings.GENERAL_FIELDS:
                    raise InvalidFieldError(field, self.site)
                if level_info['hide_admin_fields'] and field in settings.ADMIN_ONLY_FIELDS:
                    raise InvalidFieldError(field, self.site)

    def add_date_query(self, param, date):
        # strip the _year/_after/_before
        match = re.match(r'(.*)(_before|_after|_year)', param)
        if match is None:
            raise InvalidQueryError("Unknown date query '%s'." % param)
        param_prefix = match.group(1)
        solr_param = settings.DATE_PREFIX_MAPPING[param_prefix]
        if param.endswith('_year'):
            if len(date) != 4 or not date.isdigit():
                raise InvalidQueryError("Invalid year, should be 4 digits but is %s" % date)
            year = int(date)
            start_of_year = datetime(year, 1, 1, 0, 0)
            end_of_year = datetime(year, 12, 31, 23, 59)
            kwargs = {solr_param + '__range': (start_of_year, end_of_year)}
            self.si_query = self.si_query.query(**kwargs)
        else:
            if re.match(r'\d{4}-\d{2}-\d{2}', date) is None:
                raise InvalidQueryError("Invalid date, should be YYYY-MM-DD but is %s" % date)
            if param.endswith('_after'):
                kwargs = {solr_param + '__gte': date}
                self.si_query = self.si_query.query(**kwargs)
            elif param.endswith('_before'):
                kwargs = {solr_param + '__lt': date}
                self.si_query = self.si_query.query(**kwargs)
            else:
                raise InvalidQueryError("Unknown date query '%s'." % param)

    def add_filter(self, field_name, param_value):
        self.si_query = self.si_query.filter(self.add_field_query(field_name, param_value))

    def add_filter_list(self, field_name, param_value_list):
        q_final = self.solr.Q()
        for value in param_value_list:
            kwargs = {field_name: value}
            q_final = q_final | self.solr.Q(**kwargs)
        self.si_query = self.si_query.filter(q_final)

    def add_multifield_parameter_query(self, field_list, param_value):
        q_final = self.solr.Q()
        for field_name in field_list:
            q_final = q_final | self.add_field_query(field_name, param_value)
        self.si_query = self.si_query.query(q_final)

    def add_parameter_query(self, field_name, param_value):
        self.si_query = self.si_query.query(self.add_field_query(field_name, param_value))

    def add_field_query(self, field_name, param_value):
        # decode spaces and '|' before using
        decoded_param_value = urllib2.unquote(param_value)
        if not (
                decoded_param_value[0].isalnum() or
                decoded_param_value[0] == '!' or
                decoded_param_value[0] == '"'):
            raise InvalidQueryError("Cannot start query value with '%s'"
                    % decoded_param_value[0])
        tokens = self.split_string_around_quotes_and_delimiters(decoded_param_value)
        ampersand_present = '&' in tokens
        pipe_present = '|' in tokens

        if ampersand_present and pipe_present:
            raise InvalidQueryError("Cannot use both '|' and '&' within a single term")

        if pipe_present:
            q_final = self.solr.Q()
            for term in [t for t in tokens if t != '|']:
                q_final = q_final | self.get_Q(field_name, term)
        elif ampersand_present:
            q_final = self.solr.Q()
            for term in [t for t in tokens if t != '&']:
                q_final = q_final & self.get_Q(field_name, term)
        else:
            q_final = self.get_Q(field_name, param_value)

        return q_final

    def get_Q(self, field_name, value):
        if value.startswith('!'):
            kwargs = {field_name: value[1:]}
            return ~self.solr.Q(**kwargs)
        else:
            kwargs = {field_name: value}
            return self.solr.Q(**kwargs)

    # TODO: split these 2 methods into another class, along with associated
    # regex - self.quoted_re and self.amp_pipe_re
    def split_string_around_quotes_and_delimiters(self, string):
        """split string into quoted sections and on & or | outside quotes"""
        quoted_divided_string = self.quoted_re.split(string)
        # remove empty/whitespace strings
        quoted_divided_string = filter(None, [s.strip() for s in quoted_divided_string])
        # now we have quoted strings and other strings
        divided_string = []
        for str_fragment in quoted_divided_string:
            if self.is_quoted(str_fragment):
                divided_string.append(str_fragment)
            else:
                words = [w.strip() for w in self.amp_pipe_re.split(str_fragment)]
                # the filter(None, array) discards empty strings
                divided_string.extend(filter(None, words))
        return divided_string

    def is_quoted(self, string):
        if string[0] == '"' or string[:2] == '!"':
            if string[-1] == '"':
                return True
            else:
                raise InvalidQueryError('Unmatched quotes in query parameter')
        if string[-1] == '"':
            raise InvalidQueryError('Unmatched quotes in query parameter')
        else:
            return False


class FacetArgs(object):
    # what query parameter sets the sort
    SORT_QUERY_PARAM = 'count_sort'
    # the mapping from query parameter value to sort index
    SORT_MAPPING = {
        'count_desc': 'count',
        'name_asc': 'index',
    }

    def __init__(self, search_params, facet_type, facet_mapping, exclude_zero_count):
        if facet_type not in facet_mapping.keys():
            raise InvalidQueryError("Unknown count type: '%s_count'" % facet_type)
        self.mapped_facet = facet_mapping[facet_type]
        self.exclude_zero_count = exclude_zero_count
        self.search_params = search_params

    def args(self):
        return [self.mapped_facet]

    def kwargs(self):
        kwargs = {}
        self._set_mincount(kwargs)
        self._set_limit(kwargs)
        self._set_sort(kwargs)
        return kwargs

    def _set_mincount(self, kwargs):
        if self.exclude_zero_count:
            kwargs['mincount'] = 1

    def _set_limit(self, kwargs):
        if 'num_results' in self.search_params:
            kwargs['limit'] = int(self.search_params['num_results'])

    def _set_sort(self, kwargs):
        if 'count_sort' in self.search_params:
            sort_value = self.search_params['count_sort']
            if sort_value in self.SORT_MAPPING:
                kwargs['sort'] = self.SORT_MAPPING[sort_value]
            else:
                raise InvalidQueryError(
                    "count queries count_sort parameter can only have the "
                    "values %s - you gave '%s'" %
                    (
                        ', '.join(self.SORT_MAPPING.values()),
                        sort_value
                    )
                )


class SolrUnavailableError(defines.IdsApiError):
    def __init__(self, error_text=''):
        defines.IdsApiError.__init__(self, error_text)
        self.error_text = error_text


class BadRequestError(defines.IdsApiError):
    pass


class InvalidQueryError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self)
        self.error_text = 'Invalid query: ' + error_text


class InvalidOutputFormat(BadRequestError):
    def __init__(self, output_format):
        BadRequestError.__init__(self)
        self.error_text = "The output_format of data returned can be 'id', " \
            "'short', 'hub' or 'full' - you gave '%s'" % output_format


class InvalidFieldError(BadRequestError):
    def __init__(self, invalid_field, site):
        BadRequestError.__init__(self)
        self.error_text = 'Unknown field requested: %s ' % invalid_field


class UnknownQueryParamError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self)
        self.error_text = 'Unknown query parameter: ' + error_text


class UnknownObjectError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self)
        self.error_text = 'Unknown object type: ' + error_text
