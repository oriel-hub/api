# a class to build searches
#
# TODO: create a mock version of this class for tests
import urllib2
import re

import sunburnt

from openapi import defines
from django.conf import settings

query_mapping = settings.QUERY_MAPPING

class SearchBuilder():

    @classmethod
    def create_objectid_query(cls, user_level, object_id, object_type, search_params, output_format):
        for key in search_params.keys():
            if key[0] != '_' and key not in ['extra_fields']:
                raise InvalidQueryError("Unknown query parameter '%s'" % key)
        sw = SearchWrapper(user_level)
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
    def create_search(cls, user_level, search_params, object_type, output_format, facet_type=None):
        sw = SearchWrapper(user_level)

        for param in search_params:
            query_list = search_params.getlist(param)
            if len(query_list) > 1:
                raise InvalidQueryError(
                    "Cannot repeat query parameters - there is more than one '%s'" \
                    % param)
            query = query_list[0]
            if len(query) < 1:
                raise InvalidQueryError("All query parameters must have a value, but '%s' does not" % param)
            if param == 'q':
                sw.add_free_text_query(query)
            elif param in query_mapping.keys():
                if query_mapping[param]['object_type'] != 'all':
                    if query_mapping[param]['object_type'] != object_type:
                        raise InvalidQueryError(
                                "Can only use query parameter '%s' with object type '%s', your search had object type '%s'" \
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
                # params that start with _ are allowed - the django rest
                # framework deals with them
                if param[0] != '_':
                    raise UnknownQueryParamError(param)

        # always have default site
        if 'site' not in search_params:
            sw.add_parameter_query('site', 'eldis')
        sw.restrict_search_by_object(object_type)
        sw.restrict_fields_returned(output_format, search_params)
        sw.add_sort(search_params)
        if facet_type == None:
            sw.add_paginate(search_params)
        else:
            sw.add_facet(facet_type)
            sw.add_paginate({'num_results': 0})
        return sw

    @classmethod
    def create_all_search(cls, user_level, search_params, object_type, output_format):
        sw = SearchWrapper(user_level)
        sw.restrict_search_by_object(object_type)
        sw.restrict_fields_returned(output_format, search_params)
        sw.add_sort(search_params)
        sw.add_paginate(search_params)
        return sw
    
    @classmethod
    def create_category_children_search(cls, user_level, search_params, object_type, object_id):
        if object_type not in defines.OBJECT_TYPES_WITH_HIERARCHY:
            raise InvalidQueryError("Object type '%s' does not have children" % object_type)
        
        sw = SearchWrapper(user_level)
        # strip the prefix letter off
        sw.add_parameter_query('cat_parent', object_id[1:])
        sw.restrict_search_by_object(object_type)
        sw.add_paginate(search_params)
        return sw
    

class SearchWrapper:
    def __init__(self, user_level):
        try:
            self.solr = sunburnt.SolrInterface(settings.SOLR_SERVER_URL)
        except:
            raise SolrUnavailableError('Solr is not responding (using %s )' % settings.SOLR_SERVER_URL)
        self.si_query = self.solr.query()
        self.user_level = user_level

    def execute(self):
        return self.si_query.execute()

    def restrict_search_by_object(self, object_type, allow_objects=False):
        if object_type == 'assets':
            # search for any object_type that is an asset
            self.si_query = self.si_query.query(self.add_field_query('object_type', 
                '|'.join(defines.ASSET_NAMES)))
        elif allow_objects and object_type == 'objects':
            # don't restrict search and don't raise an Error
            # required for single object search
            pass
        elif object_type in defines.OBJECT_TYPES:
            self.si_query = self.si_query.query(object_type=defines.OBJECT_TYPES_TO_OBJECT_NAME[object_type])
        else:
            raise UnknownObjectError(object_type)

    def add_paginate(self, search_params):
        try:
            start_offset = int(search_params['start_offset']) if search_params.has_key('start_offset') else 0
        except ValueError:
            raise InvalidQueryError("'start_offset' must be a decimal number - you gave %s" \
                    % search_params['start_offset'])
        try:
            num_results = int(search_params['num_results']) if search_params.has_key('num_results') else 10
        except ValueError:
            raise InvalidQueryError("'num_results' must be a decimal number - you gave %s" \
                    % search_params['num_results'])
        if start_offset < 0:
            raise InvalidQueryError("'start_offset' cannot be negative - you gave %d" % start_offset)
        if num_results < 0:
            raise InvalidQueryError("'num_results' cannot be negative - you gave %d" % num_results)
        max_results = settings.USER_LEVEL_INFO[self.user_level]['max_items_per_call']
        if max_results != 0 and num_results > max_results:
            raise InvalidQueryError("'num_results' cannot be more than %d - you gave %d" \
                    % (max_results, num_results))

        if search_params.has_key('num_results_only'):
            num_results = 0
        self.si_query = self.si_query.paginate(start=start_offset, rows=num_results)

    def add_sort(self, search_params):
        if search_params.has_key('sort_asc') and search_params.has_key('sort_desc'):
            raise InvalidQueryError("Cannot use both 'sort_asc' and 'sort_desc'")
        try:
            if search_params.has_key('sort_asc'):
                if search_params['sort_asc'] not in settings.SORT_FIELDS:
                    raise InvalidQueryError("Sorry, you can't sort by %s" % search_params['sort_asc'])
                self.si_query = self.si_query.sort_by(search_params['sort_asc'])
            if search_params.has_key('sort_desc'):
                if search_params['sort_desc'] not in settings.SORT_FIELDS:
                    raise InvalidQueryError("Sorry, you can't sort by %s" % search_params['sort_desc'])
                self.si_query = self.si_query.sort_by('-' + search_params['sort_desc'])
        except sunburnt.SolrError as e:
            raise InvalidQueryError("Can't do sort - " + str(e))

    def add_free_text_query(self, search_text):
        self.si_query = self.si_query.query(search_text.lower())

    def add_facet(self, facet_type):
        if not facet_type in settings.FACET_MAPPING.keys():
            raise InvalidQueryError("Unknown count type: '%s_count'" % facet_type)
        self.si_query = self.si_query.facet_by(settings.FACET_MAPPING[facet_type])

    def restrict_fields_returned(self, output_format, search_params):
        if output_format == 'full':
            return
        # the id format needs object_type and title to construct the metadata_url
        elif output_format in [None, '', 'short', 'id']:
            field_list = ['object_id', 'object_type', 'title']
        else:
            raise InvalidQueryError(
                    "the output_format of data returned can be 'id', 'short' or 'full' - you gave '%s'" \
                    % output_format)
        if search_params.has_key('extra_fields'):
            field_list.extend(search_params['extra_fields'].lower().split(' '))
        self.si_query = self.si_query.field_limit(field_list)

    def add_date_query(self, param, date):
        # strip the _year/_after/_before
        match = re.match(r'(.*)(_before|_after|_year)', param)
        if match == None:
            raise InvalidQueryError("Unknown date query '%s'." % param)
        param_prefix = match.group(1)
        solr_param = settings.DATE_PREFIX_MAPPING[param_prefix]
        if param.endswith('_year'):
            if len(date) != 4 or not date.isdigit():
                raise InvalidQueryError("Invalid year, should be 4 digits but is %s" % date)
            year = int(date)
            kwargs = {solr_param + '__range': (str(year), str(year+1))}
            self.si_query = self.si_query.query(**kwargs)
        else:
            if re.match(r'\d{4}-\d{2}-\d{2}', date) == None:
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
        if not decoded_param_value[0].isalnum():
            raise InvalidQueryError("Cannot start query value with '%s'" \
                    % decoded_param_value[0])
        or_terms = decoded_param_value.split('|')
        and_terms = decoded_param_value.split('&')
        if len(or_terms) > 1 and len(and_terms) > 1:
            raise InvalidQueryError("Cannot use both '|' and '&' within a single term")
        if len(or_terms) > 1:
            q_final = self.solr.Q()
            for term in or_terms:
                kwargs = {field_name: term}
                q_final = q_final | self.solr.Q(**kwargs)
        elif len(and_terms) > 1:
            q_final = self.solr.Q()
            for term in and_terms:
                kwargs = {field_name: term}
                q_final = q_final & self.solr.Q(**kwargs)
        else:
            kwargs = {field_name: str(param_value)}
            q_final = self.solr.Q(**kwargs)
        return q_final

class SolrUnavailableError(defines.IdsApiError):
    def __init__(self, error_text=''):
        defines.IdsApiError.__init__(self, error_text)
        self.error_text = error_text

class BadRequestError(defines.IdsApiError):
    pass

class InvalidQueryError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self, error_text)
        self.error_text = 'Invalid query: ' + error_text

class UnknownQueryParamError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self, error_text)
        self.error_text = 'Unknown query parameter: ' + error_text

class UnknownObjectError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self, error_text)
        self.error_text = 'Unknown object type: ' + error_text
