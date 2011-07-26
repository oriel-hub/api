# some defines to use
import exceptions

URL_ROOT = '/openapi/'

OBJECT_TYPES_TO_OBJECT_NAME = {
'assets':         None,
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

OBJECT_TYPES  = OBJECT_TYPES_TO_OBJECT_NAME.keys()
OBJECT_NAMES = OBJECT_TYPES_TO_OBJECT_NAME.values()

ASSET_TYPES_TO_OBJECT_NAME = dict((k, v) for k, v in OBJECT_TYPES_TO_OBJECT_NAME.items() \
                                  if v != None and v.startswith('C'))

ASSET_TYPES  = ASSET_TYPES_TO_OBJECT_NAME.keys()
ASSET_NAMES = ASSET_TYPES_TO_OBJECT_NAME.values()

OBJECT_TYPES_WITH_HIERARCHY = ['themes', 'itemtypes']

def object_name_to_object_type(object_name):
    for object_type in OBJECT_TYPES_TO_OBJECT_NAME:
        if OBJECT_TYPES_TO_OBJECT_NAME[object_type] == object_name:
            return object_type

class IdsApiError(exceptions.StandardError):
    def __init__(self, error_text=''):
        StandardError.__init__(self)
        self.error_text = error_text
    def __str__(self):
        return self.error_text

