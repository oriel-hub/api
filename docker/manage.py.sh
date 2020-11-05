#!/bin/bash

source settings.sh

WEB_CONTAINER=`docker-compose ps -q web`

if [ -t 0 ]; then
    _DT_OPTIONS='-ti'
else
    _DT_OPTIONS='-i'
fi

docker exec ${_DT_OPTIONS} \
        ${WEB_CONTAINER} \
        sh -c "env VIRTUAL_ENV=/var/django/.ve \
              ${DJANGO_HOME}/.ve/bin/python ${DJANGO_HOME}/manage.py $@"
