from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from django.conf import settings

from sunburnt import SolrError

from openapi.data import DataMunger
from openapi.search_builder import (
    SearchBuilder, SearchParams, BadRequestError, SolrUnavailableError
)
from openapi.defines import URL_ROOT, IdsApiError
from openapi.guid_authentication import GuidAuthentication
from openapi.permissions import PerUserThrottlingRatePerGroup

from .analytics import PageViewMixin


class OpenAPIView(PageViewMixin, APIView):
    pass


class RootView(OpenAPIView):
    def get(self, request):
        hostname = request.get_host()
        url_root = 'http://' + hostname + URL_ROOT
        return Response(data={
            'help': 'http://' + hostname + '/docs/',
            'some_api_calls': {
                'all': {
                    'format': url_root + '{site}/get_all/{object_type}/{id|short|full}/',
                    'examples': [
                        url_root + 'hub/get_all/assets/short',
                        url_root + 'hub/get_all/documents/full',
                        url_root + 'hub/get_all/organisations/',
                    ]
                },
                'search': {
                    'format': url_root + '{site}/search/{object_type}/{id|short|full}/?q={query_term}&...',
                    'examples': [
                        url_root + 'hub/search/assets/?q=undp',
                        url_root + 'hub/search/documents/full?q=undp&document_published_year=2009',
                        url_root + 'hub/search/assets?country=angola%26south%20africa&theme=gender%7Cclimate%20change',
                        url_root + 'hub/search/documents/full?theme=C123|full|capacity-building-approaches',
                    ]
                },
                'object': {
                    'format': url_root + '{site}/get/{object_type}/{object_id}/{id|short|full}/friendly-name',
                    'examples': [
                        url_root + 'hub/get/assets/A12345/full',
                        url_root + 'hub/get/themes/C123/',
                        url_root + 'hub/get/themes/C123/full/capacity-building-approaches',
                    ]
                },
                'facet count': {
                    'format': url_root + 'hub/count/{object_type}/{category}/?q={query_term}&...',
                    'examples': [
                        url_root + 'hub/count/documents/theme?q=undp',
                        url_root + 'hub/count/assets/country?q=undp&document_published_year=2009',
                    ]
                },
            },
        })


class BaseAuthView(OpenAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (GuidAuthentication, SessionAuthentication)
    throttle_classes = (PerUserThrottlingRatePerGroup,)

    def __init__(self):
        super(OpenAPIView, self).__init__()
        self.site = None

    def initial(self, request, *args, **kwargs):
        self.user = request.user
        return super(BaseAuthView, self).initial(request, *args, **kwargs)

    def get_user_level_info(self):
        profile = self.user.userprofile
        return settings.USER_LEVEL_INFO[profile.user_level]

    def hide_admin_fields(self):
        return self.get_user_level_info()['hide_admin_fields']

    def general_fields_only(self):
        return self.get_user_level_info()['general_fields_only']

    def get_beacon_guid(self):
        profile = self.user.userprofile
        return profile.beacon_guid

    def setup_vars(self, request, site, output_format):
        self.user = request.user
        self.output_format = output_format
        self.site = site
        self.search_params = SearchParams(request.GET)
        self.data_munger = DataMunger(site, self.search_params)
        self.user_level = self.user.userprofile.user_level
        # note this can throw an exception, so need to catch it
        self.builder = SearchBuilder(self.user_level, site)


class BaseSearchView(BaseAuthView):

    def __init__(self, raise_if_no_results=False):
        BaseAuthView.__init__(self)
        self.output_format = None
        self.query = None
        self.raise_if_no_results = raise_if_no_results
        self.data_munger = None
        self.search_response = None

    def build_response(self):
        try:
            self.search_response, self.solr_query = self.query.execute()
        except SolrError as e:
            if str(e).find('is invalid value') != -1:
                raise IdsApiParseError('Could not parse Solr output. Original error was "%s"' % str(e))
            else:
                raise
        formatted_results = []
        for result in self.search_response:
            formatted_results.append(self.data_munger.get_required_data(result,
                self.output_format, self.get_user_level_info(), self.get_beacon_guid()))
        if self.raise_if_no_results and len(formatted_results) == 0:
            raise NoObjectFoundError()
        return formatted_results

    def format_result_list(self, request):
        # return the metadata with the output_format specified
        results = self.build_response()
        if 'num_results_only' in request.GET:
            return {'metadata': {'total_results': self.search_response.result.numFound}}

        metadata = {
            'total_results': self.search_response.result.numFound,
            'start_offset': self.search_response.result.start,
        }
        if self.next_page_available():
            metadata['next_page'] = self.generate_next_page_link(request)
        if self.prev_page_available():
            metadata['prev_page'] = self.generate_prev_page_link(request)
        if not self.hide_admin_fields():
            metadata['solr_query'] = self.solr_query
        return {'metadata': metadata, 'results': results}

    def next_page_available(self):
        last_index_on_page = self.search_response.result.start + len(list(self.search_response))
        return self.search_response.result.numFound > last_index_on_page

    def prev_page_available(self):
        return self.search_response.result.start > 0

    def generate_next_page_link(self, request):
        params = request.GET.copy()
        if 'num_results' not in params:
            params['num_results'] = '10'
        current_start_offset = int(params['start_offset']) if 'start_offset' in params else 0
        params['start_offset'] = current_start_offset + int(params['num_results'])
        return 'http://' + request.get_host() + request.path + '?' + params.urlencode()

    def generate_prev_page_link(self, request):
        params = request.GET.copy()
        if 'num_results' not in params:
            params['num_results'] = '10'
        current_start_offset = int(params['start_offset']) if 'start_offset' in params else 0
        params['start_offset'] = current_start_offset - int(params['num_results'])
        if params['start_offset'] < 0:
            params['start_offset'] = 0
        return 'http://' + request.get_host() + request.path + '?' + params.urlencode()


class ObjectView(BaseSearchView):
    def __init__(self):
        BaseSearchView.__init__(self, True)

    def get(self, request, site, object_id, output_format, object_type=None):
        try:
            self.setup_vars(request, site, output_format)
            self.query = self.builder.create_itemid_query(
                object_id, self.search_params, object_type, output_format)
        except BadRequestError as e:
            raise ValidationError(e)
        except SolrUnavailableError as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return the metadata with the output_format specified
        try:
            return Response(data={'results': self.build_response()[0]})
        except NoObjectFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND,
                    data='No %s found with item_id %s' % (object_type, object_id))


class ObjectSearchView(BaseSearchView):
    def get(self, request, site, output_format, object_type=None):
        try:
            self.setup_vars(request, site, output_format)
            if not self.search_params.has_query():
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data='object search must have some query string, eg /objects/search/short?q=undp')
            self.query = self.builder.create_search(
                self.search_params, object_type, output_format)
        except BadRequestError as e:
            return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)
        except SolrUnavailableError as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return the metadata with the output_format specified
        return Response(self.format_result_list(request))


class AllObjectView(BaseSearchView):
    def get(self, request, site, output_format, object_type=None):
        try:
            self.setup_vars(request, site, output_format)
            self.query = self.builder.create_all_search(
                self.search_params, object_type, output_format)
        except BadRequestError as e:
            raise ValidationError(e)
        except SolrUnavailableError as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=str(e))

        # return the metadata with the output_format specified
        return Response(self.format_result_list(request))


class FacetCountView(BaseAuthView):
    def get(self, request, site, object_type, facet_type):
        try:
            self.setup_vars(request, site, 'id')
            query = self.builder.create_search(
                self.search_params, object_type, 'id', facet_type)
        except BadRequestError as e:
            raise ValidationError(e)
        except SolrUnavailableError as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=str(e))
        search_response, solr_query = query.execute()
        facet_counts = search_response.facet_counts.facet_fields[settings.FACET_MAPPING[facet_type]]
        facet_dict_list = []
        for category, count in facet_counts:
            facet_dict = self.data_munger.convert_facet_string(category)
            facet_dict['count'] = count
            facet_dict_list.append(facet_dict)

        metadata = {'total_results': search_response.result.numFound}
        if not self.hide_admin_fields():
            metadata['solr_query'] = solr_query

        return Response({'metadata': metadata,
                facet_type + '_count': facet_dict_list})


class CategoryChildrenView(BaseSearchView):
    def get(self, request, site, object_type, object_id, output_format):
        try:
            self.setup_vars(request, site, output_format)
            self.query = self.builder.create_category_children_search(
                self.search_params, object_type, object_id)
        except BadRequestError as e:
            raise ValidationError(e)
        except SolrUnavailableError as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return the metadata with the output_format specified
        return Response(self.format_result_list(request))


class The404View(OpenAPIView):

    name = '404'

    def get(self, request, path):
        return Response(status=status.HTTP_404_NOT_FOUND, data="Path '%s' not known." % path)


class NoObjectFoundError(IdsApiError):
    pass


class IdsApiParseError(IdsApiError):
    pass
