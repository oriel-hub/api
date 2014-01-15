import os
from os import path
import sys
import site

vcs_root_dir = path.abspath(path.join(path.dirname(__file__), '..'))

relative_django_dir = path.join('django', 'idsapi')
relative_ve_dir = path.join(relative_django_dir, '.ve')

# ensure the virtualenv for this instance is added
python = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
site.addsitedir(
    path.join(vcs_root_dir, relative_ve_dir, 'lib', python, 'site-packages'))

sys.path.append(path.join(vcs_root_dir, relative_django_dir))

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
