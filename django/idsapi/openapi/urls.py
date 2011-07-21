from django.conf.urls.defaults import patterns, url

from openapi.views import AllObjectView, ObjectSearchView, ObjectView, FieldListView, \
    RootView, FacetCountView, CategoryChildrenView, The404View

urlpatterns = patterns('idsapi.openapi.views',

    url(r'^$', RootView.as_view(), name='root'),


    url(r'^fieldlist/?$', FieldListView.as_view(), name='field_list'),

    # eg:
    # /assets/search/short
    # /themes/search/
    # /documents/search/full
    url(r'^(?P<object_type>\w+)/search(?:/(?P<output_format>\w*)/?)?$',
        ObjectSearchView.as_view(), name='object_search'),

    # eg:
    # /themes/C34/children/full
    url(r'^(?P<object_type>\w+)/(?P<object_id>C\d+)/children(?:/(?P<output_format>\w*)/?)?$', 
        CategoryChildrenView.as_view(), name='category_children'),

    # eg:
    # /objects/A1234/full
    # /documents/A5678/
    url(r'^(?P<object_type>\w+)/(?P<object_id>[AC]\d+)(?:/(?P<output_format>\w*)(/\S*)?)?$', 
        ObjectView.as_view(), name='object'),

    # eg:
    # /assets/all/full/
    # /documents/all/
    url(r'^(?P<object_type>\w+)/all(?:/(?P<output_format>\w*)/?)?$', 
        AllObjectView.as_view(), name='all_object'),

    # eg:
    # /assets/country_count/
    # /documents/keyword_count
    url(r'^(?P<object_type>\w+)/(?P<facet_type>\w+)_count/?$', 
        FacetCountView.as_view(), name='facet_count'),

    # finally do a catch all to give a nicer 404
    url(r'^(?P<path>.+)$', The404View.as_view(), name='404'),
)
