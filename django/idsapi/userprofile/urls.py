from django.conf.urls.defaults import patterns, url

import userprofile.admin

urlpatterns = patterns('',
    url(r'^admin/user/download/$', userprofile.admin.download_view,
        name='user_list_download'),
)