#!/bin/sh

set -u

# Python3 upgrade replacement for bootstrap.py (temporary helper - likely will
# move to pipenv).

VE_PATH=../django/idsapi/.ve3
PIP=${VE_PATH}/bin/pip

${PIP} install -r pip_packages_devel.txt



