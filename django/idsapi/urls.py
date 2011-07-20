from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import openapi.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'idsapi.views.home', name='home'),
    # url(r'^idsapi/', include('idsapi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('registration.urls')),

    # the API stuff
    url(r'^openapi/', include(openapi.urls)),

    url(r'^$', redirect_to, {'url': '/openapi/'}),

)
