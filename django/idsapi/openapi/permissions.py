from rest_framework.throttling import UserRateThrottle
from rest_framework.exceptions import PermissionDenied

from django.conf import settings
from django.contrib.sites.models import Site


class PerUserThrottlingRatePerGroup(UserRateThrottle):
    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.

        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        profile = request.user.userprofile
        try:
            user_rate = settings.USER_LEVEL_INFO[profile.user_level]['max_call_rate']
        except KeyError:
            domain = Site.objects.all()[0].domain
            # The user has not completed registration
            raise PermissionDenied(detail=(
                    'You must complete registration before using the API. ',
                    'Please visit http://%s/profiles/edit/ and complete your registration.' % domain
                )
            )

        self.rate = user_rate
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super(UserRateThrottle, self).allow_request(request, view)
