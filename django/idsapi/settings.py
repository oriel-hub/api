# Settings for the openapi app

# This is used to send email alerts to the admins of the system
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Peter Mason', 'p.mason@ids.ac.uk'),
    # ('Duncan Edwards', 'd.edwards@ids.ac.uk'),
)
# Default email address
DEFAULT_FROM_EMAIL = 'd.edwards@ids.ac.uk'

# the email server at IDS
EMAIL_HOST = '139.184.194.19'

# Where to find SOLR
DEFAULT_SITE = 'eldis'
SOLR_SERVER_URLS = {
        'eldis': 'http://api.ids.ac.uk:8983/solr/eldis-test/',
        'bridge': 'http://api.ids.ac.uk:8983/solr/bridge-test/',
        }
SOLR_SCHEMA_SUFFIX = 'admin/file/?file=schema.xml'

SOLR_SCHEMA = SOLR_SERVER_URLS[DEFAULT_SITE] + SOLR_SCHEMA_SUFFIX

# whether to send solr search parameters to logs/console
# default to False - best to override in local_settings
# don't forget to turn it off again!
LOG_SEARCH_PARAMS = False

# These set the user limits
USER_LEVEL_INFO = {
        'General User': {
            'max_call_rate':     '150/hour',
            'max_items_per_call': 500,
            'image_beacon':       True,
            'hide_admin_fields':  True,
            'general_fields_only': True,
            'level':              1,
            },
        'Offline Application User': {
            'max_call_rate':     '300/hour',
            'max_items_per_call': 500,
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
DEFAULT_SORT_FIELD = 'date_created'
DEFAULT_SORT_ASCENDING = False

# these fields will be hidden from those with #'hide_admin_fields' set to True
ADMIN_ONLY_FIELDS = [
    'send_email_alerts',
    'notification_email',
    'copyright_clearance',
    'redistribute_clearance',
    'licence_type',
    'permission_to_host_info',
    'et_al',
    'legacy_id',
	'category_theme_array',
    'category_region_array',
	'category_sector',
    'category_subject',
    'timestamp',
    'publisher_id',
    'cat_level',
    'date_updated',
    ]

# these are the fields that will be given to a 'General User'
GENERAL_FIELDS = [
    'title',
    'headline',
    'long_abstract',
    'object_id',
    'object_type',
    'metadata_url',
	'author',
    'urls',
    'website_url',
    'et_al',
    'legacy_id',
	'keyword',
    'country_focus',
    'category_theme',
	'category_region',
    'category_theme_path',
	'category_theme_array',
	'publication_date',
    'publication_year',
    'publisher',
    'publisher_country',
    'item_type',
    'start_date',
    'end_date',
    'country_name',
    'iso_two_letter_code',
    'cat_parent',
    'date_created',
    'date_updated',
	'publisher_id',
    'cat_level',
	'site',
	'language_name',
	'acronym',
	'alternative_acronym',
	'alternative_name',
	'timestamp',
        ]

# these are the fields you can use for sorting
SORT_FIELDS = [
        'title',
       'asset_id',
        'category_id',
        'publication_date',
       'date_created',
        'asset_publication_date',
        'start_date',
        'end_date',
        'publisher_id',
        'acronym',
        ]

# these are fields that contain XML data
STRUCTURED_XML_FIELDS = [
        'category_theme_array',
        'publisher_array',
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
        'country': {
            'solr_field': 'country_focus',
            'object_type': 'all'
            },
        'keyword': {
            'solr_field': 'keyword',
            'object_type': 'all'
            },
        'region':  {
            'solr_field': 'category_region',
            'object_type': 'all'
            },
        'sector':  {
            'solr_field': 'category_sector',
            'object_type': 'all'
            },
        'subject': {
            'solr_field': 'category_subject',
            'object_type': 'all'
            },
        'site':  {
            'solr_field': 'site',
            'object_type': 'all'
            },
        'theme':   {
            'solr_field': 'category_theme_path',
            'object_type': 'all'
            },
        'author':  {
            'solr_field': 'author',
            'object_type': 'documents'
            },
        'publisher': {
            'solr_field': 'publisher',
            'object_type': 'documents'
            },
        'publisher_id' : {
            'solr_field': 'publisher_id',
            'object_type': 'documents',
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
        'publisher_country': {
            'solr_field': 'publisher_country',
            'object_type': 'documents',
            },
        'organisation_name': {
            'solr_field': ['title', 'alternative_name'],
            'object_type': 'organisations'
            },
        'acronym': {
            'solr_field': ['acronym', 'alternative_acronym'],
            'object_type': 'organisations'
            },
        'item_type':  {
            'solr_field': 'item_type',
            'object_type': 'items'
            },
       'cat_level':  {
            'solr_field': 'cat_level',
            'object_type': 'themes'
            },
       'theme_id':  {
            'solr_field': 'category_theme_ids',
            'object_type': 'all'
            },
        }

# this maps from the date-based query parameter to the SOLR field used
# so document_published_year would use the publication_date as the field.
DATE_PREFIX_MAPPING = {
        'metadata_published': 'asset_publication_date',
        'document_published': 'publication_date',
        'item_started': 'start_date',
        'item_finished': 'end_date',
        }

# this maps from the URL for faceted search (eg country_count) to the
# facet field used
FACET_MAPPING = {
        'country': 'country_focus_facet',
        'keyword': 'keyword_facet',
        'region':  'category_region_facet',
        'sector':  'category_sector_facet',
        'subject': 'category_subject_facet',
        'theme':   'category_theme_path_facet',
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
OBJECT_TYPES_WITH_HIERARCHY = ['themes', 'itemtypes']

######################################################################
#
# PLEASE DON'T EDIT ANYTHING BELOW HERE UNLESS YOU KNOW ABOUT DJANGO
# PROGRAMMING.
#
######################################################################

import os
#import private_settings #@UnresolvedImport

# override in local_settings if you want to
DEBUG = False
TEMPLATE_DEBUG = DEBUG

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

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
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
import private_settings
SECRET_KEY = private_settings.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'idsapi.urls'

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
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

from local_settings import *
