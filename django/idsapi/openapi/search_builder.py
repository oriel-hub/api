# a class to build searches
#
# TODO: create a mock version of this class for tests
import exceptions

import sunburnt

from openapi import defines

SOLR_SERVER_URL = 'http://api.ids.ac.uk:8983/solr/eldis-test/'

class SearchBuilder():

    def __init__(self):
        self.solr = sunburnt.SolrInterface(SOLR_SERVER_URL)
        self.si_query = None

    @classmethod
    def create_assetid_search(cls, asset_id, asset_type):
        sb = SearchBuilder()
        sb.si_query = sb.solr.query(asset_id=asset_id)
        sb.restrict_search_by_asset(asset_type)
        return sb

    @classmethod
    def create_free_text_search(cls, search_string, asset_type):
        sb = SearchBuilder()
        sb.si_query = sb.solr.query(search_string)
        sb.restrict_search_by_asset(asset_type)
        return sb

    def execute(self):
        return self.si_query.execute()

    def restrict_search_by_asset(self, asset_type):
        if asset_type != None and asset_type != 'assets':
            if not asset_type in defines.asset_types:
                raise UnknownAssetException('Incorrect asset_type: ' + asset_type)
            self.si_query = self.si_query.query(object_type=defines.asset_types_to_object_name[asset_type])



class UnknownAssetException(exceptions.Exception):
    def __init__(self, error_text='Unknown asset type'):
        Exception.__init__(self)
        self.error_text = error_text
        return
        
    def __str__(self):
        print self.error_text
