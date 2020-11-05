#!/bin/sh

# Standalone bootstrapping for fabric (for deployment when we don't want to
# bootstrap the whole project).

# apt get install libmariadb-dev-compat

PYTHON3=`which python3`
VE_PATH=.ve
VE_PYTHON="${VE_PATH}/bin/python"
VE_PIP="${VE_PYTHON} -m pip"

${PYTHON3} -m venv ${VE_PATH}

${VE_PIP} install -U pip setuptools
${VE_PIP} install wheel
${VE_PIP} install -r deploy-requirements.txt
