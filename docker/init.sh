#!/bin/bash

PYTHON_BIN="/usr/local/bin/python3"  # the real python path in our Docker image
DEPLOY_DIR=$(realpath `dirname "$0"`/../deploy)
DJANGO_DIR=$(realpath `dirname "$0"`/../django/idsapi)
DOCKER_WEB="docker-compose exec web"

CMD="all"
if [ $# -gt 0 ] ; then
    CMD="$1"
fi

do_cmd () {
	echo "do_cmd: $@"
	"$@"
	ret=$?
	if [[ $ret -eq 0 ]] ; then
		echo "Successfully ran [ $@ ]"
		else
		echo "Error: Command [ $@ ] returned $ret"
		exit $ret
	fi
}

web () {
    $DOCKER_WEB "${@}"
}

py () {
    env PYTHON_BIN=${PYTHON_BIN} ${*}
}

python_install () { 
    py ${DEPLOY_DIR}/bootstrap.py --dev -rf
}

db () {
    py ${DEPLOY_DIR}/tasks.py clean_db
    py ${DEPLOY_DIR}/tasks.py update_db:syncdb=False
    py ${DEPLOY_DIR}/tasks.py deploy:dev
    # If testing will a real db dump:
    # ../../deploy/tasks.py restore_db:/tmp/db_dump.sql
}

migrate () {
    py ${DJANGO_DIR}/manage.py migrate 
    py ${DJANGO_DIR}/manage.py check
    # Run test setup with create-db so it's created (subsequent test runs will
    # reuse the db for performance - but note this needs recreating if
    # migrations are run)
    py ${DJANGO_DIR}/manage.py test --setup-only --create-db --migrations --rootdir=${DJANGO_DIR}
}


all () {
    do_cmd python_install
    do_cmd db
    do_cmd migrate 
}

do_cmd $CMD
