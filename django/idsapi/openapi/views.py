# Create your views here.
import exceptions

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status

from openapi.data import DataMunger, DataMungerFormatException
from openapi.search_builder import SearchBuilder, UnknownAssetException, \
        InvalidQueryException, UnknownQueryParamException
from openapi.defines import URL_ROOT, get_hostname

class RootView(View):
    def get(self, request):
        hostname = get_hostname(request)
        url_root = 'http://' + hostname + URL_ROOT
        return {
            'search': {
                'format': url_root + 'assets/search/?q={query_term}',
                'example': url_root + 'assets/search/?q=undp',
                },
            'asset': {
                'format': url_root + 'assets/{asset_id}/{id|short|full}',
                'example': url_root + 'assets/12345/full',
                'example2': url_root + 'assets/123/',
                },
            'help': 'http://' + hostname + '/docs/',
            }

class BaseView(View):
    def __init__(self, raise_if_no_results=False):
        View.__init__(self)
        self.output_format = None
        self.query = None
        self.raise_if_no_results = raise_if_no_results
        self.data_munger = None

    def build_response(self):
        formatted_results = []
        try:
            for result in self.query.execute():
                formatted_results.append(self.data_munger.get_required_data(result, self.output_format))
        except DataMungerFormatException as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        if self.raise_if_no_results and len(formatted_results) == 0:
            raise NoAssetFoundException()
        return formatted_results


class AssetView(BaseView):
    def __init__(self):
        BaseView.__init__(self, True)

    def get(self, request, asset_id, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger(request)

        try:
            self.query = SearchBuilder.create_assetid_query(asset_id, asset_type)
        except (UnknownAssetException, InvalidQueryException, UnknownQueryParamException) as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)

        # return the metadata with the output_format specified
        try:
            return self.build_response()
        except NoAssetFoundException:
            return Response(status.HTTP_404_NOT_FOUND, 
                    content='No %s found with asset_id %s' % (asset_type, asset_id))


class AssetSearchView(BaseView):
    def get(self, request, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger(request)

        search_params = request.GET
        if len(search_params.keys()) == 0:
            return Response(status.HTTP_400_BAD_REQUEST, 
                    content='asset search must have some query string, eg /assets/search/short?q=undp')
        try:
            self.query = SearchBuilder.create_search(search_params, asset_type)
        except (UnknownAssetException, InvalidQueryException, UnknownQueryParamException) as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)

        # return the metadata with the output_format specified
        return self.build_response()



class NoAssetFoundException(exceptions.Exception):
    pass
