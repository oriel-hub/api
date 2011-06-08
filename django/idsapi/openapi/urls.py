from django.conf.urls.defaults import patterns, url

from idsapi.openapi.views import AssetView, AssetSearchView, CategoryView

urlpatterns = patterns('idsapi.openapi.views',
    url(r'^assets/search/(?P<amount>\w+).(?P<format>\w+)', AssetSearchView.as_view(), name='asset_search'),
    url(r'^assets/(?P<asset_id>\d+)/(?P<amount>\w+).(?P<format>\w+)', AssetView.as_view(), name='asset'),
#    url(r'^decision/add$', 'decision_add_page', name='decision_add'),
#    url(r'^decision/(?P<decision_id>[\d]+)/$', 'decision_view_page',
#                            name='decision_edit'),
#    url(r'^decision_list/(?P<group_id>[\d]+)/$',
#                                openconsent.publicweb.views.decision_list, name='decision_list'),
#    url(r'^groups/$', openconsent.publicweb.views.groups, name='groups'),
#    url(r'^group_add/$', 'group_add', name='group_add'),
)
