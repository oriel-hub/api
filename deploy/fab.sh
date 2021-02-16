env VIRTUAL_ENV=$PWD/.ve PYTHON_BIN="/usr/bin/python3" ./fab.py -p$(pass show Projects/IdsHosting/idsapi/tacuma.ids.ac.uk  |head -n1) -uroot -A $*
