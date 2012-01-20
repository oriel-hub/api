import os
import tasklib

def deploy(environment=None):
    """Do all the required steps in order"""
    if environment == None:
        environment = tasklib._infer_environment()
        if tasklib.env['verbose']:
            print "Inferred environment as %s" % environment

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
