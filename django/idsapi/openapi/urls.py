from django.conf.urls import url

from openapi.views import AllObjectView, ObjectSearchView, ObjectView, FieldListView, \
    RootView, FacetCountView, CategoryChildrenView, The404View

urlpatterns = ('idsapi.openapi.views',

    url(r'^$', RootView.as_view(), name='root'),

    url(r'^(?P<site>\w+)/fieldlist/?$', FieldListView.as_view(), name='field_list'),

    # eg:
    # /eldis/search/documents?q=undp&author=lopez
    url(r'^(?P<site>\w+)/search/(?P<object_type>\w+)(?:/(?P<output_format>\w*)/?)?$',
        ObjectSearchView.as_view(), name='object_search'),

    # eg:
    # /eldis/get_children/themes/34/full
    url(r'^(?P<site>\w+)/get_children/(?P<object_type>\w+)/(?P<object_id>[AC]\d+)(?:/(?P<output_format>\w*)/?)?$',
        CategoryChildrenView.as_view(), name='category_children'),

    # eg:
    # /eldis/get/assets/C1234/full
    # /eldis/get/countries/A1100/full
    url(r'^(?P<site>\w+)/get/(?P<object_type>\w+)/(?P<object_id>[A-Z]\d+)(?:/(?P<output_format>\w*)(/\S*)?)?$',
        ObjectView.as_view(), name='object'),

    # eg:
    # /eldis/get_all/assets/full/
    # /eldis/get_all/documents/
    url(r'^(?P<site>\w+)/get_all/(?P<object_type>\w+)(?:/(?P<output_format>\w*)/?)?$',
        AllObjectView.as_view(), name='all_object'),

    # eg:
    # /eldis/count/documents/country?q=undp
    # /assets/country_count/
    # /documents/keyword_count
    url(r'^(?P<site>\w+)/count/(?P<object_type>\w+)/(?P<facet_type>\w+)/?$',
        FacetCountView.as_view(), name='facet_count'),

    # finally do a catch all to give a nicer 404
    url(r'^(?P<path>.+)$', The404View.as_view(), name='404'),
)
