from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

import userprofile.urls
urlpatterns = userprofile.urls.urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings

import openapi.urls

from userprofile.forms import ProfileForm

urlpatterns += patterns('',
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^profiles/edit/', 'profiles.views.edit_profile',
        {'form_class': ProfileForm, 'success_url': '/profiles/view/'},
        name='edit_profile'),
    url(r'^profiles/view/', 'userprofile.views.profile_detail', name='profile_detail'),
    #url(r'^profiles/', include('profiles.urls')),

    # the API stuff
    url(r'^openapi/', include(openapi.urls)),
    url(r'^$', RedirectView.as_view(url='/about/', permanent=False)),
)
