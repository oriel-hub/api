from django.conf.urls import url

import userprofile.admin

urlpatterns = ('',
    url(r'^admin/user/download/$', userprofile.admin.download_view,
        name='user_list_download'),
)
