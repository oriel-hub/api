env VIRTUAL_ENV=$PWD/.ve ./fab.py -p$(pass show Projects/IdsHosting/idsapi/tacuma.ids.ac.uk  |head -n1) -uroot -A $*
