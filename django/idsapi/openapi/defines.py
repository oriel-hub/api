# some defines to use
URL_ROOT = '/openapi/'

asset_types = [ 'assets', 'documents', 'organisations', 'themes', 'items', 
    'subjects', 'sectors', 'countries', 'regions', 'item_types', ]

asset_types_to_object_name = {
'assets':        None,
'documents':     'CDocument',
'organisations': 'COrganisation',
'themes':        'theme',
'items':         'CItem',
'subjects':      'subject',
'sectors':       'sector',
'countries':     'CCountry',
'regions':       'region',
'item_types':    'itemtype',
}

asset_types  = asset_types_to_object_name.keys()
object_names = asset_types_to_object_name.values()

def object_name_to_asset_type(object_name):
    for asset_type in asset_types_to_object_name:
        if asset_types_to_object_name[asset_type] == object_name:
            return asset_type
    return None

def get_hostname(request):
    if request.META.has_key('HTTP_HOST'):
        return request.META['HTTP_HOST']
    elif request.META.has_key('HOST'):
        return request.META['HOST']
    else:
        return 'hostname'
