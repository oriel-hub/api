# some defines to use
import exceptions
from django.conf import settings

URL_ROOT = '/v1/'

OBJECT_TYPES = settings.OBJECT_TYPES_TO_OBJECT_NAME.keys()
OBJECT_NAMES = settings.OBJECT_TYPES_TO_OBJECT_NAME.values()

ASSET_TYPES_TO_OBJECT_NAME = dict((k, v) for k, v in settings.OBJECT_TYPES_TO_OBJECT_NAME.items()
                                if k in settings.ASSET_TYPES)

ASSET_NAMES = ASSET_TYPES_TO_OBJECT_NAME.values()


def object_name_to_object_type(object_name):
    for object_type in settings.OBJECT_TYPES_TO_OBJECT_NAME:
        if settings.OBJECT_TYPES_TO_OBJECT_NAME[object_type] == object_name:
            return object_type


class IdsApiError(exceptions.StandardError):

    def __init__(self, error_text=''):
        StandardError.__init__(self)
        self.error_text = error_text

    def __str__(self):
        return self.error_text
