from fabric.context_managers import remote_tunnel, settings
from fabric.state import env
from fabric.operations import require, prompt, get, run, sudo, local, put
from fabric.api import hide

from dye.fablib import deploy as _deploy

from dye.fablib import (
     _create_dir_if_not_exists,
     _migrate_directory_structure,
     _set_vcs_root_dir_timestamp,
     check_for_local_changes,
     create_copy_for_next,
     checkout_or_update,
     rm_pyc_files,
     create_deploy_virtualenv,
     link_webserver_conf
)

from os import path
from datetime import datetime



from fabric.contrib import files

def _exists(path, use_sudo=False, verbose=False):
    """
    Return True if given path exists on the current remote host.

    If ``use_sudo`` is True, will use `sudo` instead of `run`.

    `exists` will, by default, hide all output (including the run line, stdout,
    stderr and any warning resulting from the file not existing) in order to
    avoid cluttering output. You may specify ``verbose=True`` to change this
    behavior.

    .. versionchanged:: 1.13
        Replaced internal use of ``test -e`` with ``stat`` for improved remote
        cross-platform (e.g. Windows) compatibility.
    """
    func = use_sudo and sudo or run
    cmd = 'test -e %s' % files._expand_path(path)
    # If verbose, run normally
    if verbose:
        with settings(warn_only=True):
            return not func(cmd).failed
    # Otherwise, be quiet
    with settings(hide('everything'), warn_only=True):
        return not func(cmd).failed

# Monkey patch exists that doesn't use /usr/bin/stat (not available on
# SiteGround)
files.exists = _exists


def webserver_cmd(cmd):
    sudo("systemctl %s httpd" % cmd)

# Work around firewall restrictions preventing direct connections to github:
#
# * Tunnel github SSH connections to the deploying matchine.
#
# * Use SSH agent forwarding to provide SSH keys for github and inject them
#   into the sudoers environment. Note you must fully trust the remote host
#   with your SSH agent - suggest using agent per connection, to limit
#   potential risks around agent forwarding.
#
def deploy(revision=None, keep=None, full_rebuild=True):

    if env.environment in ['drooga', 'boorka', 'tacuma']:
        # Use adhoc tunneling to reach Git repo (bypass outbound firewall
        # rules).
        env.repository = 'ssh://git@127.0.0.1:48002/oriel-hub/api.git'
        with settings(sudo_prefix='sudo -E -s -p \'{}\''.format(env.sudo_prompt)):
            with remote_tunnel(
                48002,
                local_port=22,
                local_host='github.com',
                remote_bind_address='127.0.0.1'
                ):
                return _deploy(revision=None, keep=None, full_rebuild=True)

    return _deploy(revision=None, keep=None, full_rebuild=True)


def __deploy(revision=None, keep=None, full_rebuild=True):
    """ update remote host environment (virtualenv, deploy, update)

    It takes three arguments:

    * revision is the VCS revision ID to checkout (if not specified then
      the latest will be checked out)
    * keep is the number of old versions to keep around for rollback (default
      5)
    * full_rebuild is whether to do a full rebuild of the virtualenv
    """
    require('project_type', 'server_project_home', provided_by=env.valid_envs)

    # this really needs to be first - other things assume the directory exists
    _create_dir_if_not_exists(env.server_project_home)

    # if the <server_project_home>/previous/ directory doesn't exist, this does
    # nothing
    _migrate_directory_structure()
    _set_vcs_root_dir_timestamp()

    check_for_local_changes(revision)
    # TODO: check for deploy-in-progress.json file
    # also check if there are any directories newer than current ???
    # might just mean we did a rollback, so maybe don't bother as the
    # deploy-in-progress should be enough
    # _check_for_deploy_in_progress()

    # TODO: create deploy-in-progress.json file
    # _set_deploy_in_progress()
    create_copy_for_next()
    checkout_or_update(in_next=True, revision=revision)
    # remove any old pyc files - essential if the .py file is removed by VCS
    if env.project_type == "django":
        rm_pyc_files(path.join(env.next_dir, env.relative_django_dir))
    # create the deploy virtualenv if we use it
    create_deploy_virtualenv(in_next=True, full_rebuild=full_rebuild)

    # we only have to disable this site after creating the rollback copy
    # (do this so that apache carries on serving other sites on this server
    # and the maintenance page for this vhost)
    downtime_start = datetime.now()
    link_webserver_conf(maintenance=False)

    # TODO: do a database dump in the old directory
    point_current_to_next()

    # Use tasks.py deploy:env to actually do the deployment, including
    # creating the virtualenv if it thinks it necessary, ignoring
    # env.use_virtualenv as tasks.py knows nothing about it.
    _tasks('deploy:' + env.environment)

    # bring this vhost back in, reload the webserver and touch the WSGI
    # handler (which reloads the wsgi app)
    link_webserver_conf()
    downtime_end = datetime.now()
    touch_wsgi()

    link_cron_files()
    delete_old_rollback_versions(keep)
    if env.environment == 'production':
        setup_db_dumps()

    # TODO: _remove_deploy_in_progress()
    # move the deploy-in-progress.json file into the old directory as
    # deploy-details.json
    _report_downtime(downtime_start, downtime_end)



