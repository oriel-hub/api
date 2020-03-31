#!/bin/sh

set -u

# Python3 upgrade replacement for bootstrap.py (temporary helper - likely will
# move to pipenv).

VE_PATH=../django/idsapi/.ve3
PIP=${VE_PATH}/bin/pip

rm -rf ${VE_PATH}

python3 -m venv ${VE_PATH}

${PIP} install wheel
${PIP} install -U pip setuptools
${PIP} install -r pip_packages.txt



