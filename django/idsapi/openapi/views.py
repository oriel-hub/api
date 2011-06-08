# Create your views here.

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest

from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status
import json
import sunburnt

#from resourceexample.forms import MyForm

SOLR_SERVER_URL = 'http://api.ids.ac.uk:8983/solr/eldis-test/'

class AssetView(View):
    def get(self, request, id, amount, format):
        # find the asset with id
        # return the metadata with the amount of detail and format specified
        pass

class AssetSearchView(View):
    def get(self, request, amount, format):
        # do a search based on the stuff after ?
        search_params = request.GET
        if not search_params.has_key('q'):
            #response = HttpResponseBadRequest('asset search must have a query string, eg /assets/search/short.json?q=undp')
            #return response
            return Response(status.HTTP_400_BAD_REQUEST, 
                    content='asset search must have a query string, eg /assets/search/short.json?q=undp')
        search_string = search_params['q']
        si = sunburnt.SolrInterface(SOLR_SERVER_URL)
        r = si.query(search_string).execute()
        results = []
        for result in r:
            if amount == 'id':
                results.append({'id': result['asset_id']})
            elif amount == 'short':
                results.append({'id': result['asset_id'], 'title': result['title']})
            elif amount == 'full':
                results.append(result)
            else:
                return Response(status.HTTP_400_BAD_REQUEST, 
                        content='the amount of data returned can be "id", "short" or "full"')
        return results
#        if format == 'json':
#            return json.dumps(results)
#        else:
#            return Response(status.HTTP_400_BAD_REQUEST,
#                    content='the format of the data can only be "json" currently')

class CategoryView(View):
    pass

