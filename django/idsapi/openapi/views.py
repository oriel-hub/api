#from django.core.urlresolvers import reverse
#from django.http import HttpResponse, HttpResponseBadRequest
import httplib2
from xml.dom import minidom

from djangorestframework import status
from djangorestframework.authentication import UserLoggedInAuthentication
from djangorestframework.permissions import IsAuthenticated
from djangorestframework.response import Response
from djangorestframework.views import View

from django.conf import settings

from sunburnt import SolrError

from openapi.data import DataMunger
from openapi.search_builder import SearchBuilder, BadRequestError, SolrUnavailableError
from openapi.defines import URL_ROOT, IdsApiError
from openapi.guid_authentication import GuidAuthentication
from openapi.permissions import PerUserThrottlingRatePerGroup


class RootView(View):
    def get(self, request):
        hostname = request.get_host()
        url_root = 'http://' + hostname + URL_ROOT
        return {
            'help': 'http://' + hostname + '/docs/',
            'some_api_calls': {
                'all': {
                    'format': url_root + '{site}/get_all/{object_type}/{id|short|full}/',
                    'examples': [
                        url_root + 'eldis/get_all/assets/short',
                        url_root + 'bridge/get_all/documents/full',
                        url_root + 'eldis/get_all/organisations/',
                    ]
                },
                'search': {
                    'format': url_root + '{site}/search/{object_type}/{id|short|full}/?q={query_term}&...',
                    'examples': [
                        url_root + 'eldis/search/assets/?q=undp',
                        url_root + 'bridge/search/documents/full?q=undp&document_published_year=2009',
                        url_root + 'eldis/search/assets?country=angola%26south%20africa&theme=gender%7Cclimate%20change',
                        url_root + 'eldis/search/documents/full?theme=C123|full|capacity-building-approaches',
                    ]
                },
                'object': {
                    'format': url_root + '{site}/get/{object_type}/{object_id}/{id|short|full}/friendly-name',
                    'examples': [
                        url_root + 'eldis/get/assets/A12345/full',
                        url_root + 'eldis/get/themes/C123/',
                        url_root + 'eldis/get/themes/C123/full/capacity-building-approaches',
                    ]
                },
                'field list': {
                    'format': url_root + 'eldis/fieldlist/',
                },
                'facet count': {
                    'format': url_root + 'eldis/count/{object_type}/{category}/?q={query_term}&...',
                    'examples': [
                        url_root + 'eldis/count/documents/theme?q=undp',
                        url_root + 'bridge/count/assets/country?q=undp&document_published_year=2009',
                    ]
                },
            },
        }


class BaseAuthView(View):
    permissions = (IsAuthenticated, PerUserThrottlingRatePerGroup)
    authentication = (GuidAuthentication, UserLoggedInAuthentication)

    def __init__(self):
        View.__init__(self)
        self.site = None

    def get_user_level_info(self):
        profile = self.user.get_profile()
        return settings.USER_LEVEL_INFO[profile.user_level]

    def hide_admin_fields(self):
        return self.get_user_level_info()['hide_admin_fields']

    def general_fields_only(self):
        return self.get_user_level_info()['general_fields_only']

    def get_beacon_guid(self):
        profile = self.user.get_profile()
        return profile.beacon_guid


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
        self.output_format = output_format
        self.site = site
        self.data_munger = DataMunger(site)
        search_params = request.GET
        user_level = self.user.get_profile().user_level

        try:
            self.query = SearchBuilder.create_objectid_query(user_level, site,
                    object_id, object_type, search_params, output_format)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        try:
            return {'results': self.build_response()[0]}
        except NoObjectFoundError:
            return Response(status.HTTP_404_NOT_FOUND,
                    content='No %s found with object_id %s' % (object_type, object_id))


class ObjectSearchView(BaseSearchView):
    def get(self, request, site, output_format, object_type=None):
        self.output_format = output_format
        self.site = site
        self.data_munger = DataMunger(site)
        user_level = self.user.get_profile().user_level

        search_params = request.GET
        if len(search_params.keys()) == 0:
            return Response(status.HTTP_400_BAD_REQUEST,
                    content='object search must have some query string, eg /objects/search/short?q=undp')
        try:
            self.query = SearchBuilder.create_search(user_level, site,
                    search_params, object_type, output_format)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class AllObjectView(BaseSearchView):
    def get(self, request, site, output_format, object_type=None):
        self.output_format = output_format
        self.site = site
        self.data_munger = DataMunger(site)
        user_level = self.user.get_profile().user_level

        search_params = request.GET
        try:
            self.query = SearchBuilder.create_all_search(user_level, site,
                    search_params, object_type, output_format)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class FacetCountView(BaseAuthView):
    def get(self, request, site, object_type, facet_type):
        self.site = site
        search_params = request.GET
        user_level = self.user.get_profile().user_level
        try:
            query = SearchBuilder.create_search(user_level, site,
                    search_params, object_type, 'id', facet_type)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)
        search_response, solr_query = query.execute()
        facet_counts = search_response.facet_counts.facet_fields[settings.FACET_MAPPING[facet_type]]
        data = DataMunger(site)
        facet_dict_list = []
        for category, count in facet_counts:
            facet_dict = data.convert_facet_string(category)
            facet_dict['count'] = count
            facet_dict_list.append(facet_dict)

        metadata = {'total_results': search_response.result.numFound}
        if not self.hide_admin_fields():
            metadata['solr_query'] = solr_query

        return {'metadata': metadata,
                facet_type + '_count': facet_dict_list}


class FieldListView(BaseAuthView):
    def get(self, request, site):
        self.site = site
        # fetch file from SOLR_SCHEMA
        # TODO: Is this caching useful?
        http = httplib2.Http("/tmp/.cache")
        if site not in settings.SOLR_SERVER_INFO:
            return Response(status.HTTP_400_BAD_REQUEST, content="Unknown site: %s" % site)
        schema_url = settings.SOLR_SERVER_INFO[site]['base_url'] + settings.SOLR_SCHEMA_SUFFIX
        # TODO: Check the response code here, so that SOLR errors are gracefully handled.
        _, content = http.request(schema_url, "GET")  # @UnusedVariable
        doc = minidom.parseString(content)
        field_list = [field.getAttribute('name') for field in
                doc.getElementsByTagName('fields')[0].getElementsByTagName('field')]
        field_list.sort()
        if self.general_fields_only():
            field_list = [elem for elem in field_list if elem in settings.GENERAL_FIELDS]
        else:
            field_list = [elem for elem in field_list if not elem.endswith('_facet')]
            field_list = [elem for elem in field_list if not elem in ['text', 'word']]
            if self.hide_admin_fields():
                field_list = [elem for elem in field_list if not elem in settings.ADMIN_ONLY_FIELDS]
        return field_list


class CategoryChildrenView(BaseSearchView):
    def get(self, request, site, object_type, object_id, output_format):
        self.output_format = output_format
        self.site = site
        self.data_munger = DataMunger(site)
        user_level = self.user.get_profile().user_level

        try:
            self.query = SearchBuilder.create_category_children_search(user_level,
                    site, request.GET, object_type, object_id)
        except BadRequestError as e:
            return Response(status.HTTP_400_BAD_REQUEST, content=e)
        except SolrUnavailableError as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR, content=e)

        # return the metadata with the output_format specified
        return self.format_result_list(request)


class The404View(View):

    name = '404'

    def get(self, request, path):
        return Response(status.HTTP_404_NOT_FOUND, content="Path '%s' not known." % path)


class NoObjectFoundError(IdsApiError):
    pass


class IdsApiParseError(IdsApiError):
    pass
