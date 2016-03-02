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
from django.core.urlresolvers import reverse
from rest_framework.settings import api_settings

from openapi import defines

# this is a global to cache the Solr instance
saved_solr_interface = {}
solr_interface_created = {}

query_mapping = settings.QUERY_MAPPING

logger = logging.getLogger(__name__)
logger.setLevel(getattr(settings, 'LOG_LEVEL', logging.DEBUG))


def get_solr_interface(site):
    """cache the solr interface for an hour at a time so we don't need
    to fetch the schema on every single query."""
    global saved_solr_interface
    global solr_interface_created
    if site not in settings.SOLR_SERVER_URLS:
        raise InvalidQueryError("Unknown site: %s" % site)
    if site not in saved_solr_interface:
        too_old = True
    else:
        age = datetime.now() - solr_interface_created[site]
        too_old = age > timedelta(hours=1)
    if too_old:
        try:
            saved_solr_interface[site] = sunburnt.SolrInterface(
                settings.SOLR_SERVER_URLS[site], format='json')
            solr_interface_created[site] = datetime.now()
        except:
            raise SolrUnavailableError('Solr is not responding (using %s )' %
                                       settings.SOLR_SERVER_URLS[site])
    return saved_solr_interface[site]


class SearchBuilder():

    @classmethod
    def create_objectid_query(cls, user_level, site, object_id, object_type,
                              search_params, output_format):
        for param in search_params:
            if (param[0] != '_' and
                param != api_settings.URL_FORMAT_OVERRIDE and
                param not in ['extra_fields']
            ):
                raise InvalidQueryError("Unknown query parameter '%s'" % param)
        sw = SearchWrapper(user_level, site)
        sw.si_query = sw.solr.query(object_id=object_id)
        sw.restrict_search_by_object(object_type, allow_objects=True)
        sw.restrict_fields_returned(output_format, search_params)
        return sw

    @classmethod
    def _is_date_query(cls, param):
        for date_prefix in settings.DATE_PREFIX_MAPPING.keys():
            if param.startswith(date_prefix):
                return True
        return False

    @classmethod
    def create_search(cls, user_level, site, search_params, object_type, output_format, facet_type=None):
        sw = SearchWrapper(user_level, site)

        for param in search_params:
            query_list = search_params.getlist(param)
            if len(query_list) > 1:
                raise InvalidQueryError(
                    "Cannot repeat query parameters - there is more than one '%s'"
                    % param)
            query = query_list[0]
            if len(query) < 1:
                raise InvalidQueryError("All query parameters must have a value, but '%s' does not" % param)
            if param == 'q':
                sw.add_free_text_query(urllib.unquote_plus(query))
            elif param in query_mapping.keys():
                if query_mapping[param]['object_type'] != 'all':
                    if query_mapping[param]['object_type'] != object_type:
                        raise InvalidQueryError(
                            "Can only use query parameter '%s' with object type '%s', your search had object type '%s'"
                            % (param, query_mapping[param]['object_type'], object_type))
                # we might have to search across multiple fields
                if isinstance(query_mapping[param]['solr_field'], list):
                    sw.add_multifield_parameter_query(query_mapping[param]['solr_field'], query)
                else:
                    sw.add_parameter_query(query_mapping[param]['solr_field'], query)
            elif SearchBuilder._is_date_query(param):
                sw.add_date_query(param, query)
            # if param not in our list of allowed params
            elif not param in ['num_results', 'num_results_only', 'start_offset',
                    'extra_fields', 'sort_asc', 'sort_desc']:
                # params that start with _ are allowed, as well as the format
                # parameter - the django rest framework deals with them
                # TODO: This doesn't seem the most transparent way of handling
                # django rest framework parameters. Would it be better to
                # delete them from the request before they are passed to our
                # API code?
                if (param[0] != '_' and param != api_settings.URL_FORMAT_OVERRIDE):
                    raise UnknownQueryParamError(param)

        sw.restrict_search_by_object(object_type)
        sw.restrict_fields_returned(output_format, search_params)
        sw.add_sort(search_params, object_type)
        if facet_type is None:
            sw.add_paginate(search_params)
        else:
            sw.add_facet(facet_type, search_params)
            sw.add_paginate({'num_results': 0})
        return sw

    @classmethod
    def create_all_search(cls, user_level, site, search_params, object_type, output_format):
        sw = SearchWrapper(user_level, site)
        sw.restrict_search_by_object(object_type)
        sw.restrict_fields_returned(output_format, search_params)
        sw.add_sort(search_params, object_type)
        sw.add_paginate(search_params)
        return sw

    @classmethod
    def create_category_children_search(cls, user_level, site, search_params, object_type, object_id):
        if object_type not in settings.OBJECT_TYPES_WITH_HIERARCHY:
            raise InvalidQueryError("Object type '%s' does not have children" % object_type)

        sw = SearchWrapper(user_level, site)
        # strip the prefix letter off
        sw.add_parameter_query('cat_parent', object_id[1:])
        sw.restrict_search_by_object(object_type)
        sw.add_paginate(search_params)
        return sw


class SearchWrapper:
    quoted_re = re.compile(r'("[^"]*?")')
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
        self.si_query = self.solr.query().add_extra(defType='edismax')
        self.user_level = user_level
        self.has_free_text_query = False

    def execute(self):
        solr_query = settings.SOLR_SERVER_URLS[self.site] + 'select/?' + urllib.urlencode(self.si_query.params())
        if settings.LOG_SEARCH_PARAMS:
            # this will print to console or error log as appropriate
            logger.info("search params: " + self.si_query.params())
            logger.info("solr query: " + solr_query)
        return self.si_query.execute(), solr_query

    def restrict_search_by_object(self, object_type, allow_objects=False):
        """
            Args:
                object_type (string): The type of object to search for.
            Kwargs:
                allow_objects (bool): Set for unrestricted search over objects.
        """
        if object_type == 'assets':
            # search for any object_type that is an asset
            self.si_query = self.si_query.query(self.add_field_query('object_type',
                '|'.join(defines.ASSET_NAMES)))
        elif allow_objects and object_type == 'objects':
            # don't restrict search and don't raise an Error
            # required for single object search
            pass
        elif object_type in defines.OBJECT_TYPES:
            self.si_query = self.si_query.query(object_type=settings.OBJECT_TYPES_TO_OBJECT_NAME[object_type])
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

    def add_sort(self, search_params, object_type):
        """
            Args:
                search_params (dict): A dict like containing the request query string.
                object_type (string): The object type of the request ('asset', 'document, etc).

             do default sort order, but only if no free text query -
             if there is a free text query then the sort order will be by
             score
        """
        sort_asc = search_params.get('sort_asc')
        sort_desc = search_params.get('sort_desc')

        if sort_asc and sort_desc:
            raise InvalidQueryError("Cannot use both 'sort_asc' and 'sort_desc'")
        try:
            # Assumes both are never True
            sort_field = sort_asc or sort_desc
            ascending = bool(sort_asc)

            if sort_field and sort_field not in settings.SORT_FIELDS:
                raise InvalidQueryError("Sorry, you can't sort by %s" % sort_field)

            # Use default sort ordering when no sort parameter set
            if not sort_field:
                if self.has_free_text_query:
                    # free text queries have no default sort ordering
                    return
                # Allow per object_type defaults
                elif object_type and object_type in defines.OBJECT_TYPES:
                    object_default = settings.DEFAULT_SORT_OBJECT_MAPPING.get(object_type)
                    if object_default:
                        sort_field = object_default['field']
                        ascending = object_default['ascending']

            # Otherwise assume the catch all default
            if not sort_field:
                sort_field = settings.DEFAULT_SORT_FIELD
                ascending = settings.DEFAULT_SORT_ASCENDING

            if sort_field in settings.SORT_MAPPING:
                sort_field = settings.SORT_MAPPING[sort_field]

            sort_ord = '' if ascending else '-'
            self.si_query = self.si_query.sort_by(sort_ord + sort_field)

        except sunburnt.SolrError as e:
            raise InvalidQueryError("Can't do sort - " + str(e))

    def add_free_text_query(self, search_text):
        self.si_query = self.si_query.query(search_text.lower())
        return

    def add_facet(self, facet_type, search_params):
        if not facet_type in settings.FACET_MAPPING.keys():
            raise InvalidQueryError("Unknown count type: '%s_count'" % facet_type)
        facet_kwargs = {}
        if settings.EXCLUDE_ZERO_COUNT_FACETS:
            facet_kwargs['mincount'] = 1
        if 'num_results' in search_params:
            facet_kwargs['limit'] = int(search_params['num_results'])

        self.si_query = self.si_query.facet_by(settings.FACET_MAPPING[facet_type], **facet_kwargs)

    def restrict_fields_returned(self, output_format, search_params):
        if output_format == 'full':
            return
        # the id format needs object_type and title to construct the metadata_url
        elif output_format in [None, '', 'short', 'id']:
            field_list = ['object_id', 'object_type', 'title', 'level']
        else:
            raise InvalidQueryError(
                    "the output_format of data returned can be 'id', 'short' or 'full' - you gave '%s'"
                    % output_format)
        if 'extra_fields' in search_params:
            fields = search_params['extra_fields'].lower().split(' ')
            level_info = settings.USER_LEVEL_INFO[self.user_level]
            for field in fields:
                if level_info['general_fields_only'] and field not in settings.GENERAL_FIELDS:
                    raise InvalidFieldError(field, self.site)
                if level_info['hide_admin_fields'] and field in settings.ADMIN_ONLY_FIELDS:
                    raise InvalidFieldError(field, self.site)
            field_list.extend(search_params['extra_fields'].lower().split(' '))

        try:
            self.si_query = self.si_query.field_limit(field_list)
        except sunburnt.SolrError as e:
            raise InvalidQueryError("Can't limit Fields - " + str(e))

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
        if not (decoded_param_value[0].isalnum() or decoded_param_value[0] == '"'):
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
                kwargs = {field_name: term}
                q_final = q_final | self.solr.Q(**kwargs)
        elif ampersand_present:
            q_final = self.solr.Q()
            for term in [t for t in tokens if t != '&']:
                kwargs = {field_name: term}
                q_final = q_final & self.solr.Q(**kwargs)
        else:
            kwargs = {field_name: param_value}
            q_final = self.solr.Q(**kwargs)

        return q_final

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
        if string[0] == '"':
            if string[-1] == '"':
                return True
            else:
                raise InvalidQueryError('Unmatched quotes in query parameter')
        if string[-1] == '"':
            raise InvalidQueryError('Unmatched quotes in query parameter')
        else:
            return False


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


class InvalidFieldError(BadRequestError):
    def __init__(self, invalid_field, site):
        BadRequestError.__init__(self)
        field_list_url = reverse('field_list', kwargs={'site': site})
        self.error_text = 'Unknown field requested: %s ' % invalid_field + \
            'Please see the <a href="%s">field list</a> for a list of possible fields.' % \
            field_list_url


class UnknownQueryParamError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self)
        self.error_text = 'Unknown query parameter: ' + error_text


class UnknownObjectError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self)
        self.error_text = 'Unknown object type: ' + error_text
