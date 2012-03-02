from djangorestframework.permissions import PerUserThrottling
from djangorestframework.response import ErrorResponse
from djangorestframework import status

from django.conf import settings

class PerUserThrottlingRatePerGroup(PerUserThrottling):

    def check_permission(self, user):
        """
        Check the throttling. Different users have different rate
        limits depending on the user_level in their profile
        Return `None` or raise an :exc:`.ErrorResponse`.
        """
        profile = user.get_profile()
        try:
            rate = settings.USER_LEVEL_INFO[profile.user_level]['max_call_rate']
        except KeyError:
            # this means the user has not completed registration
            raise ErrorResponse(
                status.HTTP_403_FORBIDDEN,
                {'detail': 'You must complete registration before using the API. ' +
                           'Please visit http://api.ids.ac.uk/profiles/edit/ and complete your registration.'})
        num, period = rate.split('/')
        self.num_requests = int(num)
        if self.num_requests == 0:
            return
        self.duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]]
        self.auth = user
        self.check_throttle()
