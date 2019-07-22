from django.conf.urls import include, url
from django.conf.urls.static import static

from django.views.generic.base import RedirectView

from profiles.views import edit_profile
from userprofile.views import profile_detail
import userprofile.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.conf import settings

from userprofile.forms import ProfileForm

urlpatterns = userprofile.urls.urlpatterns
urlpatterns += [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('django_registration.backends.activation.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^profiles/edit/', edit_profile,
        {'form_class': ProfileForm, 'success_url': '/profiles/view/'},
        name='edit_profile'),
    url(r'^profiles/view/', profile_detail, name='profile_detail'),
    #url(r'^profiles/', include('profiles.urls')),

    # the API stuff
    url(r'^openapi/', include('openapi.urls')),
    #url(r'^$', RedirectView.as_view(url='/about/', permanent=False)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
