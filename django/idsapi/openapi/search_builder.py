# a class to build searches
#
# TODO: create a mock version of this class for tests
import urllib2

import sunburnt

from openapi import defines

SOLR_SERVER_URL = 'http://api.ids.ac.uk:8983/solr/eldis-test/'

query_mapping = {
        'country': 'country_focus',
        'keyword': 'keyword',
        'region': 'category_region', 
        'sector': 'category_sector', 
        'subject': 'category_subject',
        'source': 'branch', 
        'theme': 'category_theme',
        }

class SearchBuilder():

    @classmethod
    def create_assetid_query(cls, asset_id, asset_type):
        sw = SearchWrapper()
        sw.si_query = sw.solr.query(asset_id=asset_id)
        sw.restrict_search_by_asset(asset_type)
        return sw

    @classmethod
    def create_search(cls, search_params, asset_type):
        sw = SearchWrapper()

        for param in search_params:
            query_list = search_params.getlist(param)
            if len(query_list) > 1:
                raise InvalidQueryError(
                    "Cannot repeat query parameters - there is more than one '%s'" \
                    % param)
            if param == 'q':
                sw.add_free_text_query(query_list[0])
            elif param == 'all':
                if len(search_params) > 1:
                    raise InvalidQueryError(
                    "Cannot use 'all' parameter in combination with any other parameter.")
                sw.add_all_query()
            elif param in query_mapping.keys():
                sw.add_parameter_query(query_mapping[param], query_list[0])
            else:
                raise UnknownQueryParamError(param)

        sw.restrict_search_by_asset(asset_type)
        return sw


class SearchWrapper:
    def __init__(self):
        try:
            self.solr = sunburnt.SolrInterface(SOLR_SERVER_URL)
        except:
            raise SolrUnavailableError('Solr is not responding, using ' + SOLR_SERVER_URL)
        self.si_query = None

    def execute(self):
        return self.si_query.execute()

    def restrict_search_by_asset(self, asset_type):
        if asset_type != 'assets':
            if not asset_type in defines.asset_types:
                raise UnknownAssetError(asset_type)
            self.si_query = self.si_query.query(object_type=defines.asset_types_to_object_name[asset_type])

    def add_all_query(self):
        self.si_query = self.solr.query()

    def add_free_text_query(self, search_text):
        if self.si_query == None:
            self.si_query = self.solr.query(search_text)
        else:
            self.si_query = self.si_query.query(search_text)

    def add_parameter_query(self, param, param_value):
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
                kwargs = {param: term}
                q_final = q_final | self.solr.Q(**kwargs)
            self._add_combined_Qs(q_final)
        elif len(and_terms) > 1:
            q_final = self.solr.Q()
            for term in and_terms:
                kwargs = {param: term}
                q_final = q_final & self.solr.Q(**kwargs)
            self._add_combined_Qs(q_final)
        else:
            kwargs = {param: str(param_value)}
            self._add_query(**kwargs)

    def _add_query(self, **kwargs):
        if self.si_query == None:
            self.si_query = self.solr.query(**kwargs)
        else:
            self.si_query = self.si_query.query(**kwargs)

    def _add_combined_Qs(self, q_object):
        if self.si_query == None:
            self.si_query = self.solr.query(q_object)
        else:
            self.si_query = self.si_query.query(q_object)



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
