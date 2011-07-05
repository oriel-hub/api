# a class to build searches
#
# TODO: create a mock version of this class for tests
import urllib2
import re

import sunburnt

from openapi import defines
from django.conf import settings

query_mapping = {
        'country': {'solr_field': 'country_focus',    'asset_type': 'all'},
        'keyword': {'solr_field': 'keyword',          'asset_type': 'all'},
        'region':  {'solr_field': 'category_region',  'asset_type': 'all'},
        'sector':  {'solr_field': 'category_sector',  'asset_type': 'all'},
        'subject': {'solr_field': 'category_subject', 'asset_type': 'all'},
        'branch':  {'solr_field': 'branch',           'asset_type': 'all'},
        'theme':   {'solr_field': 'category_theme',   'asset_type': 'all'},
        'author':  {'solr_field': 'author',           'asset_type': 'documents'},
        'author_organisation': {'solr_field': 'author_organisation', 'asset_type': 'documents'},
        'organisation_name': {'solr_field': ['title', 'alternative_name'], 'asset_type': 'organisations'},
        'acronym': {'solr_field': ['acronym', 'alternative_acronym'], 'asset_type': 'organisations'},
        'item_type':  {'solr_field': 'item_type',     'asset_type': 'items'},
        }

date_prefix_mapping = {
        'metadata_published': 'timestamp',
        'document_published': 'publication_date',
        'item_started': 'start_date',
        'item_finished': 'end_date', 
        }

facet_mapping = {
        'country': 'country_focus_facet',
        'keyword': 'keyword_facet',
        'region':  'category_region_facet',
        'sector':  'category_sector_facet',
        'subject': 'category_subject_facet',
        'theme':   'category_theme_facet',
        }

class SearchBuilder():

    @classmethod
    def create_assetid_query(cls, asset_id, asset_type, search_params, output_format):
        for key in search_params.keys():
            if key not in ['extra_fields']:
                raise InvalidQueryError("Unknown query parameter '%s'" % key)
        sw = SearchWrapper()
        sw.si_query = sw.solr.query(asset_id=asset_id)
        sw.restrict_search_by_asset(asset_type)
        sw.restrict_fields_returned(output_format, search_params)
        return sw

    @classmethod
    def _is_date_query(cls, param):
        for date_prefix in date_prefix_mapping.keys():
            if param.startswith(date_prefix):
                return True
        return False

    @classmethod
    def create_search(cls, search_params, asset_type, output_format, facet_type=None):
        sw = SearchWrapper()

        for param in search_params:
            query_list = search_params.getlist(param)
            if len(query_list) > 1:
                raise InvalidQueryError(
                    "Cannot repeat query parameters - there is more than one '%s'" \
                    % param)
            query = query_list[0]
            if param == 'q':
                sw.add_free_text_query(query)
            elif param in query_mapping.keys():
                if query_mapping[param]['asset_type'] != 'all':
                    if query_mapping[param]['asset_type'] != asset_type:
                        raise InvalidQueryError(
                                "Can only use query parameter '%s' with asset type '%s', your had asset type '%s'" \
                                % (param, query_mapping[param]['asset_type'], asset_type))
                # we might have to search across multiple fields
                if isinstance(query_mapping[param]['solr_field'], list):
                    sw.add_multifield_parameter_query(query_mapping[param]['solr_field'], query)
                else:
                    sw.add_parameter_query(query_mapping[param]['solr_field'], query)
            elif SearchBuilder._is_date_query(param):
                sw.add_date_query(param, query)
            elif not param in ['num_results', 'num_results_only', 'start_offset', 
                    'extra_fields', 'sort_asc', 'sort_desc']:
                raise UnknownQueryParamError(param)

        sw.restrict_search_by_asset(asset_type)
        sw.restrict_fields_returned(output_format, search_params)
        sw.add_sort(search_params)
        if facet_type == None:
            sw.add_paginate(search_params)
        else:
            sw.add_facet(facet_type)
            sw.add_paginate({'num_results': 0})
        return sw

    @classmethod
    def create_all_search(cls, search_params, asset_type, output_format):
        sw = SearchWrapper()
        sw.restrict_search_by_asset(asset_type)
        sw.restrict_fields_returned(output_format, search_params)
        sw.add_paginate(search_params)
        return sw
    
    @classmethod
    def create_category_children_search(cls, search_params, asset_type, asset_id):
        if asset_type not in defines.ASSET_TYPES_WITH_HIERARCHY:
            raise InvalidQueryError("Asset type '%s' does not have children" % asset_type)
        
        sw = SearchWrapper()
        sw.add_parameter_query('cat_parent', asset_id)
        sw.restrict_search_by_asset(asset_type)
        sw.add_paginate(search_params)
        return sw
    

class SearchWrapper:
    def __init__(self):
        try:
            self.solr = sunburnt.SolrInterface(settings.SOLR_SERVER_URL)
        except:
            raise SolrUnavailableError('Solr is not responding (using %s )' % settings.SOLR_SERVER_URL)
        self.si_query = self.solr.query()

    def execute(self):
        return self.si_query.execute()

    def restrict_search_by_asset(self, asset_type):
        if asset_type != 'assets':
            if not asset_type in defines.ASSET_TYPES:
                raise UnknownAssetError(asset_type)
            self.si_query = self.si_query.query(object_type=defines.ASSET_TYPES_TO_OBJECT_NAME[asset_type])

    def add_paginate(self, search_params):
        start_offset = int(search_params['start_offset']) if search_params.has_key('start_offset') else 0
        num_results = int(search_params['num_results']) if search_params.has_key('num_results') else 10
        if start_offset < 0:
            raise InvalidQueryError("'start_offset' cannot be negative - you gave %d" % start_offset)
        if num_results < 0:
            raise InvalidQueryError("'num_results' cannot be negative - you gave %d" % num_results)
        if num_results > settings.MAX_RESULTS:
            raise InvalidQueryError("'num_results' cannot be more than %d - you gave %d" \
                    % (settings.MAX_RESULTS, num_results))
        if search_params.has_key('num_results_only'):
            num_results = 0
        self.si_query = self.si_query.paginate(start=start_offset, rows=num_results)

    def add_sort(self, search_params):
        if search_params.has_key('sort_asc') and search_params.has_key('sort_desc'):
            raise InvalidQueryError("Cannot use both 'sort_asc' and 'sort_desc'")
        try:
            if search_params.has_key('sort_asc'):
                self.si_query = self.si_query.sort_by(search_params['sort_asc'])
            if search_params.has_key('sort_desc'):
                self.si_query = self.si_query.sort_by('-' + search_params['sort_desc'])
        except sunburnt.SolrError as e:
            raise InvalidQueryError("Can't do sort - " + str(e))

    def add_free_text_query(self, search_text):
        self.si_query = self.si_query.query(search_text)

    def add_facet(self, facet_type):
        if not facet_type in facet_mapping.keys():
            raise InvalidQueryError("Unknown count type: '%s_count'" % facet_type)
        self.si_query = self.si_query.facet_by(facet_mapping[facet_type])

    def restrict_fields_returned(self, output_format, search_params):
        if output_format == 'full':
            return
        # the id format needs object_type and title to construct the metadata_url
        elif output_format in ['', 'short', 'id']:
            field_list = ['asset_id', 'object_type', 'title']
        else:
            raise InvalidQueryError(
                    "the output_format of data returned can be 'id', 'short' or 'full' - you gave '%s'" \
                    % output_format)
        if search_params.has_key('extra_fields'):
            field_list.extend(search_params['extra_fields'].split(' '))
        self.si_query = self.si_query.field_limit(field_list)

    def add_date_query(self, param, date):
        # strip the _year/_after/_before
        match = re.match(r'(.*)(_before|_after|_year)', param)
        if match == None:
            raise InvalidQueryError("Unknown date query '%s'." % param)
        param_prefix = match.group(1)
        solr_param = date_prefix_mapping[param_prefix]
        if param.endswith('_year'):
            if len(date) != 4 or not date.isdigit():
                raise InvalidQueryError("Invalid date, should be 4 digits but is %s" % date)
            year = int(date)
            kwargs = {solr_param + '__range': (str(year), str(year+1))}
            self.si_query.query(**kwargs)
        else:
            if re.match(r'\d{4}-\d{2}-\d{2}', date) == None:
                raise InvalidQueryError("Invalid date, should be YYYY-MM-DD but is %s" % date)
            if param.endswith('_after'):
                kwargs = {solr_param + '__gte': date}
                self.si_query.query(**kwargs)
            elif param.endswith('_before'):
                kwargs = {solr_param + '__lt': date}
                self.si_query.query(**kwargs)
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

class UnknownAssetError(BadRequestError):
    def __init__(self, error_text=''):
        BadRequestError.__init__(self, error_text)
        self.error_text = 'Unknown asset type: ' + error_text
