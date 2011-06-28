#from django.core.urlresolvers import reverse
#from django.http import HttpResponse, HttpResponseBadRequest

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status

from openapi.data import DataMunger, DataMungerFormatError
from openapi.search_builder import SearchBuilder, BadRequestError, SolrUnavailableError
from openapi.defines import URL_ROOT, IdsApiError

class RootView(View):
    def get(self, request):
        hostname = request.get_host()
        url_root = 'http://' + hostname + URL_ROOT
        return {
            'all': {
                'format': url_root + '{asset_type}/all/{id|short|full}',
                'examples': [
                    url_root + 'assets/all/short',
                    url_root + 'documents/all/full',
                    url_root + 'organisations/all/',
                    ]
                },
            'search': {
                'format': url_root + '{asset_type}/search/?q={query_term}&...',
                'examples': [
                    url_root + 'assets/search/?q=undp',
                    url_root + 'documents/search/?q=undp&document_published_year=2009',
                    url_root + 'assets/search/?country=angola%26south%20africa&theme=gender%7Cclimate%20change',
                    ]
                },
            'asset': {
                'format': url_root + 'assets/{asset_id}/{id|short|full}/friendly-name',
                'examples': [
                    url_root + 'assets/12345/full',
                    url_root + 'assets/123/',
                    url_root + 'themes/123/full/capacity-building-approaches',
                    ]
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
        self.search_response = None

    def build_response(self):
        formatted_results = []
        try:
            self.search_response = self.query.execute()
            for result in self.search_response:
                formatted_results.append(self.data_munger.get_required_data(result, self.output_format))
        except DataMungerFormatError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        if self.raise_if_no_results and len(formatted_results) == 0:
            raise NoAssetFoundError()
        return formatted_results

    def format_result_list(self, request):
        # return the metadata with the output_format specified
        results = self.build_response()
        # might be a HTTP 400 here
        if not isinstance(results, list):
            return results
        metadata = {
                'num_results': self.search_response.result.numFound,
                'start_offset': self.search_response.result.start,
                }
        if self.next_page_available():
            metadata['next_page'] = self.generate_next_page_link(request)
        if self.prev_page_available():
            metadata['prev_page'] = self.generate_prev_page_link(request)
        return {'metadata': metadata, 'results': results }

    def next_page_available(self):
        result = self.search_response.result
        return (result.numFound - result.start) > len(list(self.search_response))

    def prev_page_available(self):
        return self.search_response.result.start > 0

    def generate_next_page_link(self, request):
        params = request.GET.copy()
        if not params.has_key('num_results'):
            params['num_results'] = '10'
        current_start_offset = int(params['start_offset']) if params.has_key('start_offset') else 0
        params['start_offset'] = current_start_offset + int(params['num_results'])
        return 'http://' + request.get_host() + request.path + '?' + params.urlencode()

    def generate_prev_page_link(self, request):
        params = request.GET.copy()
        if not params.has_key('num_results'):
            params['num_results'] = '10'
        current_start_offset = int(params['start_offset']) if params.has_key('start_offset') else 0
        params['start_offset'] = current_start_offset - int(params['num_results'])
        if params['start_offset'] < 0:
            params['start_offset'] = 0
        return 'http://' + request.get_host() + request.path + '?' + params.urlencode()

class AssetView(BaseView):
    def __init__(self):
        BaseView.__init__(self, True)

    def get(self, request, asset_id, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger(request)

        try:
            self.query = SearchBuilder.create_assetid_query(asset_id, asset_type)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        try:
            return self.build_response()
        except NoAssetFoundError:
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
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class AllAssetView(BaseView):
    def get(self, request, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger(request)

        search_params = request.GET
        try:
            self.query = SearchBuilder.create_all_search(search_params, asset_type)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class NoAssetFoundError(IdsApiError):
    pass
