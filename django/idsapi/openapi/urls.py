from django.conf.urls.defaults import patterns, url

from openapi.views import AllAssetView, AssetSearchView, AssetView, FieldListView, \
    RootView, FacetCountView, CategoryChildrenView, The404View

urlpatterns = patterns('idsapi.openapi.views',

    url(r'^$', RootView.as_view(), name='root'),


    url(r'^fieldlist/?$', FieldListView.as_view(), name='field_list'),

    # eg:
    # /assets/search/short
    # /themes/search/
    # /documents/search/full
    url(r'^(?P<asset_type>\w+)/search(?:/(?P<output_format>\w*)/?)?$',
        AssetSearchView.as_view(), name='asset_search'),

    # eg:
    # /themes/34/children/full
    # /documents/5678/
    url(r'^(?P<asset_type>\w+)/(?P<asset_id>\d+)/children(?:/(?P<output_format>\w*)/?)?$', 
        CategoryChildrenView.as_view(), name='category_children'),

    # eg:
    # /assets/1234/full
    # /documents/5678/
    url(r'^(?P<asset_type>\w+)/(?P<asset_id>\d+)(?:/(?P<output_format>\w*)(/\S*)?)?$', 
        AssetView.as_view(), name='asset'),

    # eg:
    # /assets/all/full/
    # /documents/all/
    url(r'^(?P<asset_type>\w+)/all(?:/(?P<output_format>\w*)/?)?$', 
        AllAssetView.as_view(), name='all_asset'),

    # eg:
    # /assets/country_count/
    # /documents/keyword_count
    url(r'^(?P<asset_type>\w+)/(?P<facet_type>\w+)_count/?$', 
        FacetCountView.as_view(), name='facet_count'),

    # finally do a catch all to give a nicer 404
    url(r'^(?P<path>.+)$', The404View.as_view(), name='404'),
)
