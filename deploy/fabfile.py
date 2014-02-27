from fabric.api import *
from fabric import utils

# this is our common file that can be copied across projects
# we deliberately import all of this to get all the commands it
# provides as fabric commands
from fablib import *
import fablib

# project_settings - try not to repeat ourselves so much ...
import project_settings

env.home = '/var/django/'
env.project = project_settings.project_name
env.project_type = project_settings.project_type
# the top level directory on the server
env.project_dir = env.project

# repository type can be "svn" or "git"
env.repo_type = "git"
env.repository = 'https://github.com/oriel-hub/api.git'

env.django_dir = os.path.join('django', env.project)
env.test_cmd = ' manage.py test -v0 ' + ' '.join(project_settings.django_apps)


# does this virtualenv for python packages
env.use_virtualenv = True

# valid environments - used for require statements in fablib
env.valid_non_prod_envs = ('dev_server', 'staging_test', 'staging_new', 'staging')
env.valid_envs = ('dev_server', 'staging_test', 'staging_new', 'staging', 'production')

# does this use apache - mostly for staging_test
env.use_apache = True


# this function can just call the fablib _setup_path function
# or you can use it to override the defaults
def _local_setup():
    # put your own defaults here
    fablib._setup_path()
    # override settings here
    # if you have an ssh key and particular user you need to use
    # then uncomment the next 2 lines
    #env.user = "root"
    #env.key_filename = ["/home/shared/keypair.rsa"]


#
# These commands set up the environment variables
# to be used by later commands
#

def dev_server():
    """ use dev environment on remote host to play with code in production-like env"""
    utils.abort('remove this line when dev server setup')
    env.environment = 'dev_server'
    env.hosts = ['fen-vz-' + project_settings.project_name + '-dev']
    _local_setup()


def staging_test():
    """ use staging environment on remote host to run tests"""
    # this is on the same server as the customer facing stage site
    # so we need project_root to be different ...
    env.project_dir = env.project + '_test'
    env.environment = 'staging_test'
    env.use_apache = False
    #env.hosts = ['fen-vz-' + project_settings.project_name + '-stage']
    env.hosts = ['fen-vz-' + project_settings.project_name]
    _local_setup()


def staging():
    """ use staging environment on remote host to demo to client"""
    env.environment = 'staging'
    env.user = 'root'
    env.hosts = ['test.api.ids.ac.uk']
    _local_setup()


def staging_new():
    """ use staging environment on remote host to demo to client"""
    env.project_dir = env.project + '_new'
    env.environment = 'staging_new'
    env.user = 'root'
    env.hosts = ['test.api.ids.ac.uk']
    _local_setup()


def production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.user = 'root'
    env.hosts = ['api.ids.ac.uk']
    _local_setup()


def update_docs():
    """ update the documentation """
    require('tasks_bin', provided_by=env.valid_envs)
    sudo(env.tasks_bin + ' update_docs')
