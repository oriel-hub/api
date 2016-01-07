from rest_framework.authentication import BaseAuthentication

from userprofile.models import UserProfile

class GuidAuthentication(BaseAuthentication):
    """
    Use a GUID token
    """

    def authenticate(self, request):
        """
        Returns a tuple ( :obj:`User` , token ) if a valid GUID was supplied.
        Otherwise returns :const:`None`.
        """
        auth_token = None
        if 'HTTP_TOKEN_GUID' in request.META:
            auth_token = request.META['HTTP_TOKEN_GUID']
        elif '_token_guid' in request.GET:
            auth_token = request.GET['_token_guid']
        if auth_token:
            try:
                profile = UserProfile.objects.get(access_guid=auth_token)
                user = profile.user
                if user is not None and user.is_active:
                    return (user, None)
            except UserProfile.DoesNotExist:
                return None
        return None
