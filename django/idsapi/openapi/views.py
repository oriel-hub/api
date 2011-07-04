#from django.core.urlresolvers import reverse
#from django.http import HttpResponse, HttpResponseBadRequest
import httplib2
from xml.dom import minidom

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status

from django.conf import settings

from openapi.data import DataMunger, DataMungerFormatError
from openapi.search_builder import SearchBuilder, BadRequestError, SolrUnavailableError, \
    facet_mapping
from openapi.defines import URL_ROOT, IdsApiError, HIDDEN_FIELDS

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
            'field list': {
                'format': url_root + 'fieldlist/',
                },
            'help': 'http://' + hostname + '/docs/',
            }

class BaseSearchView(View):
    def __init__(self, raise_if_no_results=False):
        View.__init__(self)
        self.output_format = None
        self.query = None
        self.raise_if_no_results = raise_if_no_results
        self.data_munger = None
        self.search_response = None#    url(r'^decision/add$', 'decision_add_page', name='decision_add'),
#    url(r'^decision/(?P<decision_id>[\d]+)/$', 'decision_view_page',
#                            name='decision_edit'),
#    url(r'^decision_list/(?P<group_id>[\d]+)/$',
#                                openconsent.publicweb.views.decision_list, name='decision_list'),
#    url(r'^groups/$', openconsent.publicweb.views.groups, name='groups'),
#    url(r'^group_add/$', 'group_add', name='group_add'),


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
        if request.GET.has_key('num_results_only'):
            return {'metadata': {'num_results': self.search_response.result.numFound} }

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

class AssetView(BaseSearchView):
    def __init__(self):
        BaseSearchView.__init__(self, True)

    def get(self, request, asset_id, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger()
        search_params = request.GET

        try:
            self.query = SearchBuilder.create_assetid_query(asset_id, asset_type, search_params, output_format)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        try:
            return {'results': self.build_response()[0]}
        except NoAssetFoundError:
            return Response(status.HTTP_404_NOT_FOUND, 
                    content='No %s found with asset_id %s' % (asset_type, asset_id))


class AssetSearchView(BaseSearchView):
    def get(self, request, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger()

        search_params = request.GET
        if len(search_params.keys()) == 0:
            return Response(status.HTTP_400_BAD_REQUEST, 
                    content='asset search must have some query string, eg /assets/search/short?q=undp')
        try:
            self.query = SearchBuilder.create_search(search_params, asset_type, output_format)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class AllAssetView(BaseSearchView):
    def get(self, request, output_format, asset_type=None):
        self.output_format = output_format
        self.data_munger = DataMunger()

        search_params = request.GET
        try:
            self.query = SearchBuilder.create_all_search(search_params, asset_type, output_format)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class FacetCountView(View):
    def get(self, request, asset_type, facet_type):
        search_params = request.GET
        try:
            query = SearchBuilder.create_search(search_params, asset_type, 'id', facet_type)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)
        search_response = query.execute()
        facet_counts = search_response.facet_counts.facet_fields[facet_mapping[facet_type]]
        return {'metadata': {'num_results': search_response.result.numFound}, 
                facet_type+'_count': facet_counts}

class FieldListView(View):
    def get(self, request):
        # fetch file from SOLR_SCHEMA
        http = httplib2.Http(".cache")
        resp, content = http.request(settings.SOLR_SCHEMA, "GET") #@UnusedVariable
        doc = minidom.parseString(content)
        field_list = [field.getAttribute('name') for field in 
                doc.getElementsByTagName('fields')[0].getElementsByTagName('field')]
        field_list.sort()
        field_list = [elem for elem in field_list if not elem.endswith('_facet')]
        field_list = [elem for elem in field_list if not elem in ['text', 'word'] + HIDDEN_FIELDS]
        return field_list
    
class CategoryChildrenView(BaseSearchView):
    def get(self, request, asset_type, asset_id, output_format):
        self.output_format = output_format
        self.data_munger = DataMunger()

        try:
            self.query = SearchBuilder.create_category_children_search(request.GET, asset_type, asset_id)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)
        

class The404View(View):
    def get(self, request, path):
        return Response(status.HTTP_404_NOT_FOUND, content="Path '%s' not known." % path)


class NoAssetFoundError(IdsApiError):
    pass
