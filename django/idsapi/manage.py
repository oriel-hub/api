#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path
import shutil, sys, subprocess

# check python version is high enough
MIN_PYTHON_MINOR_VERSION = 6
if sys.version_info[0] != 2:
    print >> sys.stderr, "Arrggh - not using python 2.x"
    sys.exit(1)
if sys.version_info[1] < MIN_PYTHON_MINOR_VERSION:
    print >> sys.stderr, "You must use python 2.%d or later, you are using 2.%d" % (
            MIN_PYTHON_MINOR_VERSION, sys.version_info[1])
    sys.exit(1)

PROJECT_ROOT = path.abspath(path.dirname(__file__))
REQUIREMENTS = path.abspath(path.join(PROJECT_ROOT, '..', '..', 'deploy', 'pip_packages.txt'))
VE_ROOT = path.join(PROJECT_ROOT, '.ve')
VE_TIMESTAMP = path.join(VE_ROOT, 'timestamp')

ve_dir_mtime = path.exists(VE_ROOT) and path.getmtime(VE_ROOT) or 0
ve_timestamp_mtime = path.exists(VE_TIMESTAMP) and path.getmtime(VE_TIMESTAMP) or 0
reqs_timestamp = path.getmtime(REQUIREMENTS)

def ve_dir_older_than_reqs():
    return ve_dir_mtime < reqs_timestamp

def ve_timestamp_older_than_reqs():
    return ve_timestamp_mtime < reqs_timestamp

def update_ve_timestamp():
    file(VE_TIMESTAMP, 'w').close()

def go_to_ve():
    """
    If running inside virtualenv already, then just return and carry on.

    If not inside the virtualenv then call the virtualenv python, pass it
    this file and all the arguments to it, so this file will be run inside
    the virtualenv.
    """
    if not sys.prefix == VE_ROOT:
        if sys.platform == 'win32':
            python = path.join(VE_ROOT, 'Scripts', 'python.exe')
        else:
            python = path.join(VE_ROOT, 'bin', 'python')

        retcode = subprocess.call([python, __file__] + sys.argv[1:])
        sys.exit(retcode)

# manually update virtualenv?
update_ve = 'update_ve' in sys.argv or 'update_ve_quick' in sys.argv
# destroy the old virtualenv so we have a clean virtualenv?
destroy_old_ve = 'update_ve' in sys.argv

# we've been told to update the virtualenv
if update_ve:
    # if we need to create the virtualenv, then we must do that from
    # outside the virtualenv. The code inside this if statement will only
    # be run outside the virtualenv.
    if destroy_old_ve and path.exists(VE_ROOT):
        shutil.rmtree(VE_ROOT)
    if not path.exists(VE_ROOT):
        import virtualenv
        virtualenv.logger = virtualenv.Logger(consumers=[])
        #virtualenv.create_environment(VE_ROOT, site_packages=True)
        virtualenv.create_environment(VE_ROOT, site_packages=False)

    # install the pip requirements and exit
    pip_path = path.join(VE_ROOT, 'bin', 'pip')
    pip_retcode = subprocess.call([pip_path, 'install',
            '--requirement=%s' % REQUIREMENTS ])
    if pip_retcode == 0:
        update_ve_timestamp()
    sys.exit(pip_retcode)
# else if it appears that the virtualenv is out of date:
elif ve_dir_older_than_reqs() or ve_timestamp_older_than_reqs():
    print "VirtualEnv need to be updated"
    print 'Run "./manage.py update_ve" (or "./manage.py update_ve_quick")'
    sys.exit(1)

# now we should enter the virtualenv. We will only get
# this far if the virtualenv is up to date.
go_to_ve()

# run django - the usual manage.py stuff
from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
