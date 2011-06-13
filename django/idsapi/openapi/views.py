# Create your views here.

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status
import json
import sunburnt

from openapi import defines
from openapi.data import DataMunger, DataMungerFormatException
from openapi.search_builder import SearchBuilder, UnknownAssetException

#from resourceexample.forms import MyForm

SOLR_SERVER_URL = 'http://api.ids.ac.uk:8983/solr/eldis-test/'

class AssetView(View):
    def get(self, request, asset_id, output_format, asset_type=None):
        # find the asset with id
        try:
            q = SearchBuilder.create_assetid_search(asset_id, asset_type)
        except UnknownAssetException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)

        # return the metadata with the output_format specified
        r = q.execute()
        results = []
        try:
            for result in r:
                results.append(DataMunger.get_required_data(result, output_format))
        except DataMungerFormatException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        return results

class AssetSearchView(View):
    def get(self, request, output_format, asset_type=None):
        # do a search based on the stuff after ?
        search_params = request.GET
        if not search_params.has_key('q'):
            return Response(status.HTTP_400_BAD_REQUEST, 
                    content='asset search must have a query string, eg /assets/search/short?q=undp')
        try:
            q = SearchBuilder.create_free_text_search(search_params['q'], asset_type)
        except UnknownAssetException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        r = q.execute()
        results = []
        try:
            for result in r:
                results.append(DataMunger.get_required_data(result, output_format))
        except DataMungerFormatException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        return results

class CategoryView(View):
    pass

