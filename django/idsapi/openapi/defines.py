# some defines to use
import exceptions

URL_ROOT = '/openapi/'

ASSET_TYPES_TO_OBJECT_NAME = {
'assets':        None,
'documents':     'CDocument',
'organisations': 'COrganisation',
'themes':        'theme',
'items':         'CItem',
'subjects':      'subject',
'sectors':       'sector',
'countries':     'CCountry',
'regions':       'region',
'itemtypes':     'itemtype',
}

ASSET_TYPES  = ASSET_TYPES_TO_OBJECT_NAME.keys()
OBJECT_NAMES = ASSET_TYPES_TO_OBJECT_NAME.values()

ASSET_TYPES_WITH_HIERARCHY = ['themes', 'itemtypes']

HIDDEN_FIELDS = ['send_email_alerts']

def object_name_to_asset_type(object_name):
    for asset_type in ASSET_TYPES_TO_OBJECT_NAME:
        if ASSET_TYPES_TO_OBJECT_NAME[asset_type] == object_name:
            return asset_type

class IdsApiError(exceptions.StandardError):
    def __init__(self, error_text=''):
        StandardError.__init__(self)
        self.error_text = error_text
    def __str__(self):
        return self.error_text

