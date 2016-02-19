# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.http import HttpResponse

from server_tracking.google.parameters import CustomDimensionUrlGenerator
from server_tracking.parameters import VP
from server_tracking.django.settings import SERVER_SIDE_TRACKING as SST_SETTINGS
from server_tracking.django.utils import get_default_parameters, default_client


log = logging.getLogger(__name__)


class CustomDimensionParams(CustomDimensionUrlGenerator):
    guid = VP(1)


class PageViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        response = super(PageViewMixin, self).dispatch(request, *args, **kwargs)
        param_response = response if isinstance(response, HttpResponse) else None
        if not request.is_ajax():
            path = request.path_info.lstrip('/')
            if not any(path.startswith(exclude) for exclude in SST_SETTINGS['pageview_exclude']):
                misc_parameters = []

                # Track authenticated users
                if hasattr(request, 'user'):
                    try:
                        guid = request.user.userprofile.access_guid
                        misc_parameters.append(CustomDimensionParams(guid=guid))
                    except Exception as e:
                        log.exception(e)

                try:
                    pageview_params, session_params = get_default_parameters(request, param_response)
                    default_client.pageview(
                        params=pageview_params,
                        session_params=session_params,
                        misc_params=misc_parameters
                     )
                except Exception as e:
                    log.exception(e)
        return response
