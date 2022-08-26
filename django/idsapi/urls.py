from django.conf.urls import include, re_path
from django.conf.urls.static import static

from profiles.views import edit_profile
from userprofile.views import profile_detail
import userprofile.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from django.conf import settings

from userprofile.forms import ProfileForm

admin.autodiscover()
urlpatterns = userprofile.urls.urlpatterns
urlpatterns += [
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls),

    re_path(r'^accounts/',
            include('django_registration.backends.activation.urls')),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),

    re_path(r'^profiles/edit/', edit_profile,
            {'form_class': ProfileForm, 'success_url': '/profiles/view/'},
            name='edit_profile'),
    re_path(r'^profiles/view/', profile_detail, name='profile_detail'),
    # re_path(r'^profiles/', include('profiles.urls')),

    # the API stuff
    re_path(r'^openapi/', include('openapi.urls')),
    # re_path(r'^$', RedirectView.as_view(url='/about/', permanent=False)),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
