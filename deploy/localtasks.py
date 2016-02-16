from __future__ import unicode_literals, absolute_import

import os
import tasklib
from dye.tasklib.environment import env
from dye.tasklib import tasklib
from project_settings import django_apps


def post_deploy(environment):
    update_docs()

def update_docs():
    """Generate the documentation using sphinx"""
    if not env['quiet']:
        print "### Regenerating the documentation"
    docs_dir = os.path.join(env['vcs_root_dir'], 'docs')
    docs_env = os.environ
    docs_env['PATH'] = os.path.join(env['ve_dir'], 'bin') + ':' + os.environ['PATH']
    # use virtualenv and call 'make html'
    if env['quiet']:
        docs_env['SPHINXOPTS'] = '-q'
    tasklib._call_wrapper(['make', 'html'], cwd=docs_dir, env=docs_env)


def _install_django_jenkins():
    """ ensure that pip has installed the django-jenkins thing """
    if not env['quiet']:
        print "### Installing Jenkins packages"
    pip_bin = os.path.join(env['ve_dir'], 'bin', 'pip')
    cmds = [
        # django-jenkins after 0.14 require django>=1.4, so pin to 0.14
        [pip_bin, 'install', 'django-jenkins==0.14'],
        [pip_bin, 'install', 'pylint==1.3'],
        [pip_bin, 'install', 'astroid==1.2.1'],
        [pip_bin, 'install', 'coverage']]

    for cmd in cmds:
        tasklib._call_wrapper(cmd)


def _manage_py_jenkins(apps_to_test):
    """ run the jenkins command """
    args = ['jenkins', ]
    args += ['--pylint-rcfile', os.path.join(env['vcs_root_dir'], 'jenkins', 'pylint.rc')]
    coveragerc_filepath = os.path.join(env['vcs_root_dir'], 'jenkins', 'coverage.rc')
    if os.path.exists(coveragerc_filepath):
        args += ['--coverage-rcfile', coveragerc_filepath]
    args += apps_to_test
    if not env['quiet']:
        print "### Running django-jenkins, with args; %s" % args
    tasklib._manage_py(args, cwd=env['vcs_root_dir'])


def run_jenkins(apps_to_test=None, local_settings='jenkins'):
    """ make sure the local settings is correct and the database exists """
    if apps_to_test is None:
        apps_to_test = django_apps
    env['verbose'] = True
    tasklib.update_ve()
    _install_django_jenkins()
    tasklib.create_private_settings()
    tasklib.link_local_settings(local_settings)
    tasklib.clean_db()
    tasklib.update_db()
    _manage_py_jenkins(apps_to_test)


def run_jenkins_fast():
    fast_django_apps = [a for a in django_apps if 'integration' not in a]
    run_jenkins(fast_django_apps, 'jenkins_fast')


def run_jenkins_full():
    run_jenkins()
