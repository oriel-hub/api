# Settings for the openapi app

from local_settings import SERVER_ENV

# This is used to send email alerts to the admins of the system
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Peter Mason', 'p.mason@ids.ac.uk'),
    # ('Duncan Edwards', 'd.edwards@ids.ac.uk'),
)
MANAGERS = ADMINS

# Default email address
DEFAULT_FROM_EMAIL = 'api@ids.ac.uk'
SERVER_EMAIL = 'api@ids.ac.uk'

# the email server at IDS
EMAIL_HOST = 'mailrelay.ids.ac.uk'

# Where to find SOLR - note that these are over-written in the local settings
# files and are here for reference
DEFAULT_SITE = 'eldis'

if SERVER_ENV == "production":
    SOLR_SERVER_URLS = {
        'eldis': 'http://solr.ids.ac.uk:8983/solr/eldis-live/',
        'bridge': 'http://solr.ids.ac.uk:8983/solr/bridge-live/',
        'bridge_plus': 'http://solr.ids.ac.uk:8983/solr/bridge-live-plus/',
    }
elif SERVER_ENV in ["staging"]:
    SOLR_SERVER_URLS = {
        'eldis': 'http://test.api.ids.ac.uk:8983/solr/eldis-dev/',
        'bridge': 'http://test.api.ids.ac.uk:8983/solr/bridge-dev/',
        'bridge_plus': 'http://test.api.ids.ac.uk:8983/solr/bridge-dev-plus/',
    }
elif SERVER_ENV in ["localdev"]:
    SOLR_SERVER_URLS = {
        'eldis': 'http://localhost:8983/solr/eldis-test/',
        'bridge': 'http://localhost:8983/solr/bridge-test/',
    }

SOLR_SCHEMA_SUFFIX = 'admin/file/?file=schema.xml'

SOLR_SCHEMA = SOLR_SERVER_URLS[DEFAULT_SITE] + SOLR_SCHEMA_SUFFIX

# whether to send solr search parameters to logs/console
# default to False - best to override in local_settings
# don't forget to turn it off again!
LOG_SEARCH_PARAMS = False

# These set the user limits
EXCLUDE_ZERO_COUNT_FACETS = True

USER_LEVEL_INFO = {
    'General User': {
        'max_call_rate':     '150/hour',
        'max_items_per_call': 2000,
        'image_beacon':       True,
        'hide_admin_fields':  True,
        'general_fields_only': True,
        'level':              1,
    },
    'Offline Application User': {
        'max_call_rate':     '300/hour',
        'max_items_per_call': 2000,
        'image_beacon':       True,
        'hide_admin_fields':  True,
        'general_fields_only': False,
        'level':              2,
    },
    'Partner': {
        'max_call_rate':     '300/hour',
        'max_items_per_call': 2000,
        'image_beacon':       True,
        'hide_admin_fields':  True,
        'general_fields_only': False,
        'level':              3,
    },
    'Unlimited': {
        'max_call_rate':      None, # unlimited
        'max_items_per_call': 0,
        'image_beacon':       False,
        'hide_admin_fields':  False,
        'general_fields_only': False,
        'level':              4,
    },
}

# this is the default sort field
DEFAULT_SORT_FIELD = 'title'
DEFAULT_SORT_ASCENDING = True

# object type sort field mapping, overrides DEFAULT_SORT_FIELD and
# DEFAULT_SORT_ASCENDING for matching object types.
DEFAULT_SORT_OBJECT_MAPPING = {
    'documents':
        {'field': 'date_updated', 'ascending': False},
    'organisations':
        {'field': 'date_updated', 'ascending': False},
    'items':
        {'field': 'date_updated', 'ascending': False},
    'themes':
        {'field': 'category_path_sort', 'ascending': True},
    'subjects':
        {'field': 'category_path_sort', 'ascending': True},
}

# these are the fields you can use for sorting
SORT_FIELDS = [
'title',
'title_sort',
'name',
'asset_id',
'object_id',
'category_id',
'category_path',
'category_path_sort',
'publication_date',
'date_created',
'start_date',
'end_date',
'acronym',
'timestamp',
'score',
]

# these fields will be hidden from those with #'hide_admin_fields' set to True
ADMIN_ONLY_FIELDS = [
'asset_id',
'author_array',
'copyright_clearance',
'deleted',
'end_date',
'item_type',
'item_type_id',
'legacy_id',
'notification_email',
'permission_to_host_info',
'redistribute_clearance',
'send_email_alerts',
'start_date',
'title_sort',
'category_path_sort',
'publication_country_id'        
]

# these are the fields that will be given to a 'General User'
GENERAL_FIELDS = [
'acronym',
'asset_id',
'alternative_acronym',
'alternative_name',
'archived',
'author',
'author_array',
'cat_level',
'category_id',
'category_path',
'category_region_array',
'category_region_ids',
'category_region_path',
'category_theme',
'category_theme_array',
'category_theme_ids',
'category_theme_path',
'category_subject',
'category_subject_array',
'category_subject_ids',
'category_subject_path',
'children_object_array',
'country_focus',
'country_focus_array',
'country_focus_ids',
'country_name',
'date_created',
'date_updated',
'description',
'document_type',
'corporate_author',
'et_al',
'headline',
'iso_number',
'iso_three_letter_code',
'iso_two_letter_code',
'keyword',
'language_id',
'language_name',
'language_array',
'level',
'licence_type',
'address1',
'address2',
'address3',
'address4',
'address5',
'town',
'postcode',
'location_country',
'metadata_url',
'metadata_languages',
'name',
'object_id',
'object_type',
'organisation_type',
'organisation_url',
'parent_object_array',
'parent_object_id',
'publication_date',
'publication_year',
'publisher',
'publisher_array',
'publisher_country',
'publisher_id',
'publication_country_id',
'site',
'superparent_object_id',
'timestamp',
'title',
'toplevel_object_id',
'urls',
'website_url',
]

# these are fields that contain XML data
STRUCTURED_XML_FIELDS = [
'category_theme_array',
'category_subject_array',
'publisher_array',
'country_focus_array',
'category_region_array',
'children_object_array',
'parent_object_array',
'language_array',
'author_array',
]

# these are the entries in the dropdown box for user registration
ORGANISATION_TYPES = [
u'Bilateral Aid Agency',
u'Multilateral Aid Agency',
u'International NGO or CSO',
u'National / Local NGO or CSO',
u'National / Local Government',
u'Political Party',
u'Academic',
u'School / college',
u'Library / Information Service',
u'Commercial / Business',
u'Health Centre / Hospital',
u'Media',
u'Network',
u'No affiliation',
u'Other (please specify',
]

# this is the URL used for the image beacon stuff
IMAGE_BEACON_STUB_URL = 'http://api.ids.ac.uk/tracking/trackimg.cfm'

# this maps from the query parameter used in the URL to:
# * the name (or names) of the field in SOLR to search across
# * the type of object you can use the query parameter with
QUERY_MAPPING = {
    'object_id':  {
        'solr_field': 'object_id',
        'object_type': 'all'
    },
    'object_type':  {
        'solr_field': 'object_type',
        'object_type': 'all'
    },
    'asset_id':  {
        'solr_field': 'asset_id',
        'object_type': 'all'
    },
    'title':  {
        'solr_field': 'title',
        'object_type': 'all'
    },
    'country': {
        'solr_field': 'country_focus_facet',
        'object_type': 'all'
    },
    'keyword': {
        'solr_field': 'keyword',
        'object_type': 'all'
    },
    'region':  {
        'solr_field': 'category_region_facet',
        'object_type': 'all'
    },
    'sector':  {
        'solr_field': 'category_sector',
        'object_type': 'all'
    },
    'subject': {
        'solr_field': 'category_subject_facet',
        'object_type': 'all'
    },
    'subject_name': {
        'solr_field': 'category_subject_objects',
        'object_type': 'all'
    },
    'subject_id': {
        'solr_field': 'category_subject_ids',
        'object_type': 'documents'
    },
    'site':  {
        'solr_field': 'site',
        'object_type': 'all'
    },
    'category_path':   {
        'solr_field': 'category_path_sort',
        'object_type': 'all'
    },
    'theme':   {
        'solr_field': 'category_theme_facet',
        'object_type': 'all'
    },
    'theme_name':   {
        'solr_field': 'category_theme_objects',
        'object_type': 'all'
    },
    'author':  {
        'solr_field': 'author',
        'object_type': 'documents'
    },
    'publisher_name': {
        'solr_field': 'publisher',
        'object_type': 'documents'
    },
    'publisher': {
        'solr_field': 'publisher_id',
        'object_type': 'documents'
    },
    'copyright_clearance': {
        'solr_field': 'copyright_clearance',
        'object_type': 'documents',
    },
    'redistribute_clearance': {
        'solr_field': 'redistribute_clearance',
        'object_type': 'documents',
    },
    'licence_type': {
        'solr_field': 'licence_type',
        'object_type': 'all',
    },
    'permission_to_host_info': {
        'solr_field': 'permission_to_host_info',
        'object_type': 'all',
    },
    'related_information_links': {
        'solr_field': 'related_information_links',
        'object_type': 'all',
    },
    'language_name': {
        'solr_field': 'language_name',
        'object_type': 'documents',
    },
    'language': {
        'solr_field': 'metadata_languages',
        'object_type': 'documents',
    },
    'publisher_country': {
        'solr_field': 'publisher_country',
        'object_type': 'documents',
    },
    'organisation_name': {
        'solr_field': ['name', 'alternative_name'],
        'object_type': 'organisations'
    },
    'acronym': {
        'solr_field': ['acronym', 'alternative_acronym'],
        'object_type': 'organisations'
    },
    'location_country': {
        'solr_field': 'location_country',
        'object_type': 'organisations',
    },
    'item_type':  {
        'solr_field': 'item_type',
        'object_type': 'items'
    },
    'cat_level':  {
        'solr_field': 'cat_level',
        'object_type': 'all'
    },
    'deleted':  {
        'solr_field': 'deleted',
        'object_type': 'all'
    },
    'archived':  {
        'solr_field': 'archived',
        'object_type': 'all'
    },
    'level':  {
        'solr_field': 'cat_level',
        'object_type': 'all'
    },
    'cat_autocomplete':  {
        'solr_field': 'category_path_autocomplete',
        'object_type': 'all'
    },
    'title_autocomplete':  {
        'solr_field': 'title_autocomplete',
        'object_type': 'all'
    },
    'parent_object_id':  {
        'solr_field': 'parent_object_id',
        'object_type': 'all'
    },
    'first_parent_object_id':  {
        'solr_field': 'cat_first_parent',
        'object_type': 'all'
    },
    'toplevel_object_id':  {
        'solr_field': 'toplevel_object_id',
        'object_type': 'all'
    },
    'country_code':  {
        'solr_field': 'iso_two_letter_code',
        'object_type': 'countries'
    },
    'url':  {
        'solr_field': 'urls',
        'object_type': 'documents'
    },
    'document_type':  {
        'solr_field': 'document_type',
        'object_type': 'documents'
    },
}

# this maps from the date-based query parameter to the SOLR field used
# so document_published_year would use the publication_date as the field.
DATE_PREFIX_MAPPING = {
    'metadata_published': 'date_created',
    'metadata_updated': 'date_updated',
    'timestamp': 'timestamp',
    'document_published': 'publication_date',
    'item_started': 'start_date',
    'item_finished': 'end_date',
}

DATE_FIELDS = [v for k, v in DATE_PREFIX_MAPPING.items()]

# this maps from the URL for faceted search (eg country_count) to the
# facet field used
FACET_MAPPING = {
    'country':   'country_focus_objects_facet',
    'keyword':   'keyword_facet',
    'region':    'category_region_objects_facet',
    'sector':    'category_sector_facet',
    'subject':   'category_subject_objects_facet',
    'theme':     'category_theme_objects_facet',
    'publisher': 'publisher_facet',
    'publisher_country': 'publisher_country_facet',
    'publication_year': 'publication_year_facet',
    'language': 'metadata_languages',
    'document_type': 'document_type_facet',
}

# values are 'plain_string', 'id_name_type' or 'xml_string'
FACET_TYPES = {
    'country':   'xml_string',
    'keyword':   'plain_string',
    'region':    'id_name_type',
    'sector':    'plain_string',
    'subject':   'xml_string',
    'theme':     'xml_string',
    'publisher': 'plain_string',
    'publisher_country': 'plain_string',
    'publication_year': 'plain_string',
    'language': 'plain_string',
    'document_type': 'plain_string',
}

# this maps sort fields when generating SOLR queries, so that custom (eg non
# tokenized) fields can be used.
SORT_MAPPING = {
    'title': 'title_sort',
    'category_path': 'category_path_sort',
}

# the mapping of how the api refers to objects, to the object name
# in SOLR
OBJECT_TYPES_TO_OBJECT_NAME = {
    'assets':         None,
    'documents':     'Document',
    'organisations': 'Organisation',
    'themes':        'theme',
    'items':         'Item',
    'subjects':      'subject',
    'sectors':       'sector',
    'countries':     'Country',
    'regions':       'region',
    'itemtypes':     'itemtype',
}

# the list of objects that are actually assets
ASSET_TYPES = [
    'documents',
    'organisations',
    'items',
    'countries',
]

# the object types where we actually show the heirarchy
OBJECT_TYPES_WITH_HIERARCHY = ['themes', 'subjects', 'itemtypes']
