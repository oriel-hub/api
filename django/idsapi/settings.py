# Settings for the openapi app

# This is used to send email alerts to the admins of the system
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Peter Mason', 'p.mason@ids.ac.uk'),
    # ('Duncan Edwards', 'd.edwards@ids.ac.uk'),
)
# Default email address
DEFAULT_FROM_EMAIL = 'api@ids.ac.uk'

# the email server at IDS
EMAIL_HOST = 'mailrelay.ids.ac.uk'

# Where to find SOLR - note that these are over-written in the local settings
# files and are here for reference
DEFAULT_SITE = 'eldis'

SOLR_SERVER_INFO = {
    'eldis': {
        'base_url': 'http://test.api.ids.ac.uk:8983/solr/eldis-test/',
        'dismax': True,
        'name_field': 'title',
        'sort_mapping': {
            'title': 'title_sort',
            'category_path': 'category_path_sort',
        },
    },
    'bridge': {
        'base_url': 'http://test.api.ids.ac.uk:8983/solr/bridge-test/',
        'dismax': True,
        'name_field': 'title',
        'sort_mapping': {
            'title': 'title_sort',
            'category_path': 'category_path_sort',
        },
    },
    'hub': {
        'base_url': 'http://test.api.ids.ac.uk:8983/solr/oriel-searchapi-test/',
        'dismax': True,
        'name_field': 'name',
        'sort_mapping': {
            'title': 'title_en',
            'category_path': 'category_path_sort',
        },
    },
}

SOLR_SCHEMA_SUFFIX = 'admin/file/?file=schema.xml'
SOLR_SCHEMA = SOLR_SERVER_INFO[DEFAULT_SITE]['base_url'] + SOLR_SCHEMA_SUFFIX

# we have multiple "indexes" created by drupal, the one we want to use is
# this one:
SOLR_INDEX_ID = 'ids_ks_item_sources_index'

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
        'max_call_rate':      '0/sec',
        'max_items_per_call': 0,
        'image_beacon':       False,
        'hide_admin_fields':  False,
        'general_fields_only': False,
        'level':              4,
    },
}

# this is the default sort field
DEFAULT_SORT_FIELD = 'title_sort_hub_en'
DEFAULT_SORT_ASCENDING = True

# object type sort field mapping, overrides DEFAULT_SORT_FIELD and
# DEFAULT_SORT_ASCENDING for matching object types.
DEFAULT_SORT_ITEM_MAPPING = {
    'documents':
        {'field': 'date_updated_sort_hub_zz', 'ascending': False},
    'organisations':
        {'field': 'date_updated_sort_hub_zz', 'ascending': False},
    'items':
        {'field': 'date_updated_sort_hub_zz', 'ascending': False},
    'themes':
        {'field': 'category_path_sort', 'ascending': True},
    'subjects':
        {'field': 'category_path_sort', 'ascending': True},
}

# these are the fields you can use for sorting
SORT_FIELDS = [
    'title',
    'title_sort_hub_en',
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
'category_path_sort'
]

# these are the fields that will be given to a 'General User'
GENERAL_FIELDS = [
'acronym',
'alternative_acronym',
'alternative_name',
'archived',
'author',
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
'corporate_author',
'et_al',
'headline',
'iso_number',
'iso_three_letter_code',
'iso_two_letter_code',
'item_id',
'item_type',
'keyword',
'language_id',
'language_name',
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
'name',
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
'site',
'superparent_object_id',
'timestamp',
'title',
'toplevel_object_id',
'urls',
'website_url'
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
        'item_type': 'all'
    },
    'item_type':  {
        'solr_field': 'item_type',
        'item_type': 'all'
    },
    'asset_id':  {
        'solr_field': 'asset_id',
        'item_type': 'all'
    },
    'title':  {
        'solr_field': 'title',
        'item_type': 'all'
    },
    'country': {
        'solr_field': 'country_focus_facet',
        'item_type': 'all'
    },
    'keyword': {
        'solr_field': 'keyword',
        'item_type': 'all'
    },
    'region':  {
        'solr_field': 'category_region_facet',
        'item_type': 'all'
    },
    'sector':  {
        'solr_field': 'category_sector',
        'item_type': 'all'
    },
    'subject': {
        'solr_field': 'category_subject_facet',
        'item_type': 'all'
    },
    'subject_name': {
        'solr_field': 'category_subject_objects',
        'item_type': 'all'
    },
    'subject_id': {
        'solr_field': 'category_subject_ids',
        'item_type': 'documents'
    },
    'site':  {
        'solr_field': 'site',
        'item_type': 'all'
    },
    'category_path':   {
        'solr_field': 'category_path_sort',
        'item_type': 'all'
    },
    'theme':   {
        'solr_field': 'category_theme_facet',
        'item_type': 'all'
    },
    'theme_name':   {
        'solr_field': 'category_theme_objects',
        'item_type': 'all'
    },
    'author':  {
        'solr_field': 'author_search_hub_zz',
        'item_type': 'documents'
    },
    'publisher_name': {
        'solr_field': 'publisher',
        'item_type': 'documents'
    },
    'publisher': {
        'solr_field': 'publisher_id',
        'item_type': 'documents'
    },
    'copyright_clearance': {
        'solr_field': 'copyright_clearance',
        'item_type': 'documents',
    },
    'redistribute_clearance': {
        'solr_field': 'redistribute_clearance',
        'item_type': 'documents',
    },
    'licence_type': {
        'solr_field': 'licence_type',
        'item_type': 'all',
    },
    'permission_to_host_info': {
        'solr_field': 'permission_to_host_info',
        'item_type': 'all',
    },
    'related_information_links': {
        'solr_field': 'related_information_links',
        'item_type': 'all',
    },
    'language_name': {
        'solr_field': 'language_name',
        'item_type': 'documents',
    },
    'publisher_country': {
        'solr_field': 'publisher_country',
        'item_type': 'documents',
    },
    'organisation_name': {
        'solr_field': ['name', 'alternative_name'],
        'item_type': 'organisations'
    },
    'acronym': {
        'solr_field': ['acronym', 'alternative_acronym'],
        'item_type': 'organisations'
    },
    'location_country': {
        'solr_field': 'location_country',
        'item_type': 'organisations',
    },
    'item_type':  {
        'solr_field': 'item_type',
        'item_type': 'items'
    },
    'cat_level':  {
        'solr_field': 'cat_level',
        'item_type': 'all'
    },
    'deleted':  {
        'solr_field': 'deleted',
        'item_type': 'all'
    },
    'archived':  {
        'solr_field': 'archived',
        'item_type': 'all'
    },
    'cat_autocomplete':  {
        'solr_field': 'category_path_autocomplete',
        'item_type': 'all'
    },
    'level':  {
        'solr_field': 'cat_level',
        'item_type': 'all'
    },
    'title_autocomplete':  {
        'solr_field': 'title_autocomplete',
        'item_type': 'all'
    },
    'parent_object_id':  {
        'solr_field': 'parent_object_id',
        'item_type': 'all'
    },
    'toplevel_object_id':  {
        'solr_field': 'toplevel_object_id',
        'item_type': 'all'
    },
    'country_code':  {
        'solr_field': 'iso_two_letter_code',
        'item_type': 'countries'
    },
    'url':  {
        'solr_field': 'urls',
        'item_type': 'documents'
    },
    'source': {
        'solr_field': 'sources',
        'item_type': 'all',
    },
    'language': {
        'solr_field': 'metadata_languages',
        'item_type': 'all',
    },
    'publication_date': {
        'solr_field': 'publication_date_sort_hub_zz',
        'item_type': 'documents',
    }
}

# fields to use fq queries for
FQ_FIELDS = [
    'item_type',
    'country',
    'object_type',
    'metadata_languages',
    'sources',
    'keyword_search',
    'licence_type',
]

# this maps from the date-based query parameter to the SOLR field used
# so document_published_year would use the publication_date as the field.
DATE_PREFIX_MAPPING = {
    'metadata_published': 'date_created',
    'metadata_updated': 'date_updated',
    'timestamp': 'timestamp',
    'document_published': 'publication_date_sort_hub_zz',
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
    'publication_year': 'publication_year_facet'
}

# this maps sort fields when generating SOLR queries, so that custom (eg non
# tokenized) fields can be used.
SORT_MAPPING = {
    'title': 'title_sort',
    'category_path': 'category_path_sort',
}

# the mapping of how the api refers to objects, to the object name
# in SOLR
ITEM_TYPES_TO_ITEM_NAME = {
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
ITEM_TYPES_WITH_HIERARCHY = ['themes', 'subjects', 'itemtypes']

# objects that we will get back from solr, but that we should ignore
IGNORE_FIELDS = [
    'content',
    'id',
    'index_id',
    'spell',
]

# fields that will exist for all items
GENERIC_FIELD_LIST = [
    'item_id',
    'item_type',
    'metadata_languages',
    'sources',
    'timestamp',
]

SOLR_UNIQUE_KEY = 'item_id'

######################################################################
#
# PLEASE DON'T EDIT ANYTHING BELOW HERE UNLESS YOU KNOW ABOUT DJANGO
# PROGRAMMING.
#
######################################################################

import os
import sys
#import private_settings #@UnresolvedImport

# override in local_settings if you want to
DEBUG = False
TEMPLATE_DEBUG = DEBUG

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))

MANAGERS = ADMINS

ALLOWED_HOSTS = [
    '.api.ids.ac.uk',
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_HOME, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
import private_settings
SECRET_KEY = private_settings.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_HOME, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django_countries',
    'profiles',
    'registration',

    # Tom Christie REST framework
    'djangorestframework',

    # our code
    'openapi',
    'userprofile',
)

# settings required for extra fields for users
AUTH_PROFILE_MODULE = "userprofile.UserProfile"

# settings required for django registration
ACCOUNT_ACTIVATION_DAYS = 7

# standard user setting
LOGIN_REDIRECT_URL = '/profiles/view/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

from local_settings import *
