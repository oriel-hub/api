import os
import tasklib
from .project_settings import django_apps


def deploy(environment=None):
    """Do all the required steps in order"""
    if environment is None:
        environment = tasklib._infer_environment()
        if tasklib.env['verbose']:
            print "Inferred environment as %s" % environment

    tasklib.create_private_settings()
    tasklib.link_local_settings(environment)
    tasklib.create_ve()
    tasklib.update_db()
    update_docs()


def update_docs():
    """Generate the documentation using sphinx"""
    if not tasklib.env['quiet']:
        print "### Regenerating the documentation"
    docs_dir = os.path.join(tasklib.env['project_dir'], 'docs')
    docs_env = os.environ
    docs_env['PATH'] = os.path.join(tasklib.env['ve_dir'], 'bin') + ':' + os.environ['PATH']
    # use virtualenv and call 'make html'
    if tasklib.env['quiet']:
        docs_env['SPHINXOPTS'] = '-q'
    tasklib._call_wrapper(['make', 'html'], cwd=docs_dir, env=docs_env)


def _manage_py_jenkins(apps_to_test):
    """ run the jenkins command """
    args = ['jenkins', ]
    args += ['--pylint-rcfile', os.path.join(tasklib.env['project_dir'], 'jenkins', 'pylint.rc')]
    coveragerc_filepath = os.path.join(tasklib.env['project_dir'], 'jenkins', 'coverage.rc')
    if os.path.exists(coveragerc_filepath):
        args += ['--coverage-rcfile', coveragerc_filepath]
    args += apps_to_test
    if not tasklib.env['quiet']:
        print "### Running django-jenkins, with args; %s" % args
    tasklib._manage_py(args, cwd=tasklib.env['project_dir'])


def run_jenkins(apps_to_test=None):
    """ make sure the local settings is correct and the database exists """
    if apps_to_test is None:
        apps_to_test = django_apps
    tasklib.env['verbose'] = True
    tasklib.update_ve()
    tasklib._install_django_jenkins()
    tasklib.create_private_settings()
    tasklib.link_local_settings('jenkins')
    tasklib.clean_db()
    tasklib.update_db()
    _manage_py_jenkins(apps_to_test)


def run_jenkins_fast():
    run_jenkins(['openapi', 'userprofile'])


def run_jenkins_full():
    run_jenkins(['openapi', 'userprofile', 'openapi_integration'])
