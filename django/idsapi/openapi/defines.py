# some defines to use

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

asset_types = asset_types_to_object_name.keys()
