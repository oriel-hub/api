#!/bin/sh

. ./settings.sh

docker-compose exec web /bin/bash -c "cd ${DJANGO_HOME} ; $PROJECT_ROOT/docker/init.sh $*"
