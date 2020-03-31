#!/bin/sh

# Python3 replacement for legacy bootstrap.py 

PYTHON_3=`which python3.6`

# If set add WSGI baseline (production only)
if [ -z "${WSGI_BASELINE}" ] ; then
    BASELINE_VE_PATH=~/django/baseline_venv/
    BASELINE_VE_PYTHON="${BASELINE_VE_PATH}/bin/python"
    BASELINE_VE_PIP="${BASELINE_VE_PYTHON} -m pip"

    if [ ! -d "${BASELINE_VE_PATH}" ] ; then
        ${PYTHON_3} -m venv ${BASELINE_VE_PATH}
        ${BASELINE_VE_PIP} install wheel
        ${BASELINE_VE_PIP} install -U pip setuptools
    fi
fi


VE_PATH=../django/idsapi/.ve
VE_PYTHON="${VE_PATH}/bin/python"
VE_PIP="${VE_PYTHON} -m pip"

${BASELINE_VE_PYTHON} -m venv --clear ${VE_PATH}
${VE_PIP} install -U pip setuptools
${VE_PIP} install wheel
${VE_PIP} install -r pip_packages.txt

if [[ `basename $0` == "bootstrap_dev.sh" ]]; then
    ${VE_PIP} install -r pip_packages_devel.txt
fi
