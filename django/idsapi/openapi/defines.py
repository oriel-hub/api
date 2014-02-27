# some defines to use
import exceptions
from django.conf import settings

URL_ROOT = '/v1/'

ITEM_TYPES = settings.ITEM_TYPES_TO_ITEM_NAME.keys()
ITEM_NAMES = settings.ITEM_TYPES_TO_ITEM_NAME.values()

ASSET_TYPES_TO_ITEM_NAME = dict((k, v) for k, v in settings.ITEM_TYPES_TO_ITEM_NAME.items()
                                if k in settings.ASSET_TYPES)

ASSET_NAMES = ASSET_TYPES_TO_ITEM_NAME.values()


def item_name_to_item_type(item_name):
    for item_type in settings.ITEM_TYPES_TO_ITEM_NAME:
        if settings.ITEM_TYPES_TO_ITEM_NAME[item_type] == item_name:
            return item_type


class IdsApiError(exceptions.StandardError):

    def __init__(self, error_text=''):
        StandardError.__init__(self)
        self.error_text = error_text

    def __str__(self):
        return self.error_text
