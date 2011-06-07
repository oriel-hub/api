import os, sys

# find the project name from project_settings

wsgi_dir = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.abspath(os.path.join(wsgi_dir, '..', 'deploy')))
from project_settings import project_name

sys.path.append(os.path.abspath(os.path.join(wsgi_dir, '..', 'django')))
sys.path.append(os.path.abspath(os.path.join(wsgi_dir, '..', 'django', project_name)))

#print >> sys.stderr, sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = project_name + '.settings'

# this basically does:
# os.environ['PROJECT_NAME_HOME'] = '/var/django/project_name/dev/'
os.environ[project_name.upper() + '_HOME'] = os.path.join('/var/django', project_name, 'dev')

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()

