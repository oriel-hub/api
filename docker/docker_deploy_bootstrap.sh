#!/bin/sh

source settings.sh

docker-compose exec web /bin/bash -c "$PROJECT_ROOT/deploy/bootstrap.py $*"
