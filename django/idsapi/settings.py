# Build paths inside the project like this: path.join(BASE_DIR, ...)


from os import path
BASE_DIR = path.abspath(path.dirname(__file__))

import sys

########## DEFAULT DEBUG SETTINGS - OVERRIDE IN local_settings
DEBUG = False
ASSETS_DEBUG = DEBUG
ASSETS_AUTO_BUILD = DEBUG
##########


########## DATABASES are configured in local_settings.py.*


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
import private_settings
SECRET_KEY = private_settings.SECRET_KEY
########## END SECRET CONFIGURATION


########## MANAGER/EMAIL CONFIGURATION
# These email addresses will get all the error email for the production server
# (and any other servers with DEBUG = False )
# See settings_api.py
########## END MANAGER/EMAIL CONFIGURATION


########## GENERAL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#time-zone

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# Language code for this installation. All choices can be found here:
# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English')
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
########## END GENERAL CONFIGURATION





########## MEDIA CONFIGURATION
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = path.join(BASE_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = path.join(BASE_DIR, 'static')

# URL prefix for static files.
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(BASE_DIR, 'media'),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    # 'django_assets.finders.AssetsFinder',
    #
)
########## END STATIC FILE CONFIGURATION


LOCALE_DIR = path.join(BASE_DIR, 'locale')
if path.isdir(LOCALE_DIR):
    LOCALE_PATHS = (LOCALE_DIR,)


########## APP CONFIGURATION
DJANGO_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin
    #
    'django.contrib.admin',
]

THIRD_PARTY_APPS = [
    'django_countries',
    'django_registration',
    'rest_framework',
    'corsheaders',
]

# Apps specific for this project go here.
LOCAL_APPS = [
    'profiles',
    'openapi',
    'userprofile',
    'frontend_widget',
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
########## END APP CONFIGURATION

########## MIDDLEWARE CONFIGURATION
MIDDLEWARE = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
)
########## END MIDDLEWARE CONFIGURATION


########## URL Configuration
ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
# WSGI_APPLICATION = 'wsgi.application'
########## END URL Configuration


CORS_ALLOW_ALL_ORIGINS = True
CORS_URLS_REGEX = r'^/openapi/.*$'
CORS_ALLOW_METHODS = ['GET']


########## django-secure - intended for sites that use SSL
SECURE = False
if SECURE:
    INSTALLED_APPS += ("djangosecure",)

    # set this to 60 seconds and then to 518400 when you can prove it works
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_FRAME_DENY = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_SSL_REDIRECT = True
########## end django-secure


MIGRATION_MODULES = {
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    MIGRATION_MODULES['resources'] = 'resources.test_migrations'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
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
        'openapi.analytics': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # from http://stackoverflow.com/a/25114003/3189
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}

#--------------------------------
# local settings import
# from http://djangosnippets.org/snippets/1873/
#--------------------------------
try:
    import local_settings
except ImportError:
    print("""
    -------------------------------------------------------------------------
    You need to create a local_settings.py file. Run ../../deploy/tasks.py
    deploy:<whatever> to use one of the local_settings.py.* files as your
    local_settings.py, and create the database and tables mentioned in it.
    -------------------------------------------------------------------------
    """)
    import sys
    sys.exit(1)
else:
    # Import any symbols that begin with A-Z. Append to lists, or update
    # dictionaries for any symbols that begin with "EXTRA_".
    import re
    for attr in dir(local_settings):
        match = re.search('^EXTRA_(\w+)', attr)
        if match:
            name = match.group(1)
            value = getattr(local_settings, attr)
            try:
                original = globals()[name]
                if isinstance(original, collections.Mapping):
                    update_recursive(original, value)
                else:
                    original += value
            except KeyError:
                globals()[name] = value
        elif re.search('^[A-Z]', attr):
            globals()[attr] = getattr(local_settings, attr)

########## END LOCAL_SETTINGS


# import this after local_settings, so the SERVER_ENV setting will
# be available
from settings_api import *

##### from here on is stuff that depends on the value of DEBUG
##### which is set in LOCAL_SETTINGS

########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.api.ids.ac.uk',
    '.api.okhub.org',
    'drooga.ids.ac.uk',
    'idsapi.testdns.aptivate.org',
    'boorka.ids.ac.uk',
    'tacuma.ids.ac.uk'
]
########## END SITE CONFIGURATION


########## TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-TEMPLATES

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
        path.join(BASE_DIR, 'templates')
    ],
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.request'
        ],
        'debug': DEBUG,
        'loaders': [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]
    }
}]

# required for the ssi tag, used to include a standard menu
ALLOWED_INCLUDE_ROOTS = ('/var/www/includes/',)

if DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
else:
    TEMPLATES[0]['OPTIONS']['loaders'] = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )
########## END TEMPLATE CONFIGURATION

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'machina_attachments': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp',
    }
}

########## Your stuff: Below this line define 3rd party libary settings

REST_FRAMEWORK = {
    'UNICODE_JSON': False,
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework_xml.parsers.XMLParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
    ),
}

# settings required for extra fields for users
AUTH_PROFILE_MODULE = "userprofile.UserProfile"

# settings required for django registration
ACCOUNT_ACTIVATION_DAYS = 7

# standard user setting
LOGIN_REDIRECT_URL = '/profiles/view/'
