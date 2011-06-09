# Create your views here.

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status
import json
import sunburnt

from openapi import defines
from openapi.data import DataMunger

#from resourceexample.forms import MyForm

SOLR_SERVER_URL = 'http://api.ids.ac.uk:8983/solr/eldis-test/'

class AssetView(View):
    def get(self, request, asset_id, output_format, asset_type=None):
        # find the asset with id
        si = sunburnt.SolrInterface(SOLR_SERVER_URL)
        q = si.query(asset_id=asset_id)
        if asset_type != None and asset_type != 'assets':
            q = q.query(object_type=defines.asset_types_to_object_name[asset_type])

        # return the metadata with the output_format specified
        r = q.execute()
        results = []
        try:
            for result in r:
                results.append(DataMunger.get_required_data(result, output_format))
        except TypeError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        return results

class AssetSearchView(View):
    def get(self, request, output_format, asset_type=None):
        # do a search based on the stuff after ?
        search_params = request.GET
        if not search_params.has_key('q'):
            return Response(status.HTTP_400_BAD_REQUEST, 
                    content='asset search must have a query string, eg /assets/search/short?q=undp')
        search_string = search_params['q']
        si = sunburnt.SolrInterface(SOLR_SERVER_URL)
        q = si.query(search_string)
        if asset_type != None and asset_type != 'assets':
            if not asset_type in defines.asset_types:
                return Response(status.HTTP_400_BAD_REQUEST, content='Incorrect asset_type: ' + asset_type)
            q = q.query(object_type=defines.asset_types_to_object_name[asset_type])
        r = q.execute()
        results = []
        try:
            for result in r:
                results.append(DataMunger.get_required_data(result, output_format))
        except DataMungerFormatError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e.value)
        return results

class CategoryView(View):
    pass

