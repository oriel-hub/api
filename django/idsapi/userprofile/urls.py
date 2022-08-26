from django.conf.urls import re_path

import userprofile.admin

urlpatterns = [
    re_path(r'^admin/user/download/$', userprofile.admin.download_view,
            name='user_list_download'),
]
