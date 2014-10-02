from djangorestframework.permissions import PerUserThrottling
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from django.conf import settings
from django.contrib.sites.models import Site

class PerUserThrottlingRatePerGroup(PerUserThrottling):

    def check_permission(self, user):
        """
        Check the throttling. Different users have different rate
        limits depending on the user_level in their profile
        Return `None` or raise an :exc:`.ErrorResponse`.
        """
        profile = user.get_profile()
        domain = Site.objects.all()[0].domain
        try:
            rate = settings.USER_LEVEL_INFO[profile.user_level]['max_call_rate']
        except KeyError:
            # this means the user has not completed registration
            raise ErrorResponse(
                status.HTTP_403_FORBIDDEN,
                {'detail': 'You must complete registration before using the API. ' +
                           'Please visit http://%s/profiles/edit/ and complete your registration.' % domain})
        num, period = rate.split('/')
        self.num_requests = int(num)
        if self.num_requests == 0:
            return
        self.duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        self.auth = user
        self.check_throttle()
