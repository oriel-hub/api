from fabric.context_managers import settings, remote_tunnel
from fabric.state import env

from dye.fablib import deploy as _deploy

#
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
    env.repository = 'ssh://git@127.0.0.1:48002/oriel-hub/api.git'
    with settings(sudo_prefix='sudo -E -s -p \'{}\''.format(env.sudo_prompt)):
        with remote_tunnel(
            48002,
            local_port=22,
            local_host='github.com',
            remote_bind_address='127.0.0.1'
            ):
            return _deploy(revision=None, keep=None, full_rebuild=True)


