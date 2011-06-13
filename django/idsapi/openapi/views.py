# Create your views here.

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status
import sunburnt

import defines
from data import DataMunger, DataMungerFormatException
from search_builder import SearchBuilder, UnknownAssetException

class BaseView(View):
    def __init__(self):
        self.output_format = None
        self.query = None

    def build_response(self):
        formatted_results = []
        try:
            for result in self.query.execute():
                formatted_results.append(DataMunger.get_required_data(result, self.output_format))
        except DataMungerFormatException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        return formatted_results


class AssetView(BaseView):
    def get(self, request, asset_id, output_format, asset_type=None):
        self.output_format = output_format

        try:
            self.query = SearchBuilder.create_assetid_search(asset_id, asset_type)
        except UnknownAssetException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)

        # return the metadata with the output_format specified
        return self.build_response()


class AssetSearchView(BaseView):
    def get(self, request, output_format, asset_type=None):
        self.output_format = output_format

        search_params = request.GET
        if not search_params.has_key('q'):
            return Response(status.HTTP_400_BAD_REQUEST, 
                    content='asset search must have a query string, eg /assets/search/short?q=undp')
        try:
            self.query = SearchBuilder.create_free_text_search(search_params['q'], asset_type)
        except UnknownAssetException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)

        # return the metadata with the output_format specified
        return self.build_response()
