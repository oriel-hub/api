from django.conf.urls.defaults import patterns, url

from openapi.views import AssetView, AssetSearchView, RootView

urlpatterns = patterns('idsapi.openapi.views',
    # eg:
    # /assets/search/short
    # /themes/search/
    # /documents/search/full
    url(r'^(?P<asset_type>\w+)/search/(?P<output_format>\w*)$', 
        AssetSearchView.as_view(), name='asset_search'),
    # eg:
    # /assets/1234/full
    # /documents/5678/
    url(r'^(?P<asset_type>\w+)/(?P<asset_id>\d+)/(?P<output_format>\w*)$', 
        AssetView.as_view(), name='asset'),


    url(r'^$', RootView.as_view(), name='root'),

#    url(r'^decision/add$', 'decision_add_page', name='decision_add'),
#    url(r'^decision/(?P<decision_id>[\d]+)/$', 'decision_view_page',
#                            name='decision_edit'),
#    url(r'^decision_list/(?P<group_id>[\d]+)/$',
#                                openconsent.publicweb.views.decision_list, name='decision_list'),
#    url(r'^groups/$', openconsent.publicweb.views.groups, name='groups'),
#    url(r'^group_add/$', 'group_add', name='group_add'),
)
